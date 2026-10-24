"""Check that the web screens use design tokens and nothing external.

Scans every .css and .html file under apps/web (CSS in <style> blocks and style="" attributes
too). The tokens file (apps/web/assets/design-tokens.css), fonts.css, bundled font files and
tests folders are exempt. Rules:
  raw-colour         hex, rgb(), hsl() and similar, or a named colour such as red
  raw-type           font-size, font-family or font shorthand that is not a token
  raw-radius         a non-zero border radius that is not a token
  undefined-token    var(--name) where --name is defined nowhere
  external-resource  a URL, @import, src or href that leaves the device (no CDN)

Run: python scripts/check_design_tokens.py [--root PATH]. Exit code 1 if anything is found.
Not covered: colours written inside JavaScript strings.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

WEB = "apps/web"
EXEMPT = {"apps/web/assets/design-tokens.css", "apps/web/assets/fonts.css"}
SKIP_DIRS = {"tests", "fonts", "node_modules", ".git", "__pycache__"}

NAMED_COLOURS = set(
    [
        "aliceblue",
        "antiquewhite",
        "aqua",
        "aquamarine",
        "azure",
        "beige",
        "bisque",
        "black",
        "blanchedalmond",
        "blue",
        "blueviolet",
        "brown",
        "burlywood",
        "cadetblue",
        "chartreuse",
        "chocolate",
        "coral",
        "cornflowerblue",
        "cornsilk",
        "crimson",
        "cyan",
        "darkblue",
        "darkcyan",
        "darkgoldenrod",
        "darkgray",
        "darkgreen",
        "darkgrey",
        "darkkhaki",
        "darkmagenta",
        "darkolivegreen",
        "darkorange",
        "darkorchid",
        "darkred",
        "darksalmon",
        "darkseagreen",
        "darkslateblue",
        "darkslategray",
        "darkslategrey",
        "darkturquoise",
        "darkviolet",
        "deeppink",
        "deepskyblue",
        "dimgray",
        "dimgrey",
        "dodgerblue",
        "firebrick",
        "floralwhite",
        "forestgreen",
        "fuchsia",
        "gainsboro",
        "ghostwhite",
        "gold",
        "goldenrod",
        "gray",
        "green",
        "greenyellow",
        "grey",
        "honeydew",
        "hotpink",
        "indianred",
        "indigo",
        "ivory",
        "khaki",
        "lavender",
        "lavenderblush",
        "lawngreen",
        "lemonchiffon",
        "lightblue",
        "lightcoral",
        "lightcyan",
        "lightgoldenrodyellow",
        "lightgray",
        "lightgreen",
        "lightgrey",
        "lightpink",
        "lightsalmon",
        "lightseagreen",
        "lightskyblue",
        "lightslategray",
        "lightslategrey",
        "lightsteelblue",
        "lightyellow",
        "lime",
        "limegreen",
        "linen",
        "magenta",
        "maroon",
        "mediumaquamarine",
        "mediumblue",
        "mediumorchid",
        "mediumpurple",
        "mediumseagreen",
        "mediumslateblue",
        "mediumspringgreen",
        "mediumturquoise",
        "mediumvioletred",
        "midnightblue",
        "mintcream",
        "mistyrose",
        "moccasin",
        "navajowhite",
        "navy",
        "oldlace",
        "olive",
        "olivedrab",
        "orange",
        "orangered",
        "orchid",
        "palegoldenrod",
        "palegreen",
        "paleturquoise",
        "palevioletred",
        "papayawhip",
        "peachpuff",
        "peru",
        "pink",
        "plum",
        "powderblue",
        "purple",
        "rebeccapurple",
        "red",
        "rosybrown",
        "royalblue",
        "saddlebrown",
        "salmon",
        "sandybrown",
        "seagreen",
        "seashell",
        "sienna",
        "silver",
        "skyblue",
        "slateblue",
        "slategray",
        "slategrey",
        "snow",
        "springgreen",
        "steelblue",
        "tan",
        "teal",
        "thistle",
        "tomato",
        "turquoise",
        "violet",
        "wheat",
        "white",
        "whitesmoke",
        "yellow",
        "yellowgreen",
    ]
)
COLOUR_PROPS = re.compile(
    r"^(color|fill|stroke|box-shadow|text-shadow|caret-color|accent-color|scrollbar-color|"
    r"background(-color|-image)?|border(-[a-z]+)*|outline(-[a-z]+)*|text-decoration(-color)?|"
    r"column-rule(-color)?|--[\w-]+)$"
)
HEX = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b")
COLOUR_FUNC = re.compile(r"\b(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch)\(", re.IGNORECASE)
LENGTH = re.compile(r"(?<![\w.-])(\d*\.?\d+)(?:px|rem|em|pt|vw|vh|vmin|vmax|%)")
SIZE_WORDS = re.compile(
    r"\b(?:xx-small|x-small|small|medium|large|x-large|xx-large|xxx-large|smaller|larger)\b"
)
KEYWORDS = {"", "inherit", "initial", "unset", "revert"}
DECLARATION = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;{}]*)")
EXTERNAL = re.compile(
    r"""url\(\s*["']?\s*(?:https?:)?//|@import\s+(?:url\(\s*)?["']?\s*(?:https?:)?//"""
    r"""|\b(?:src|href)\s*=\s*["']\s*(?:https?:)?//""",
    re.IGNORECASE,
)
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
STYLE_ATTR = re.compile(r"""\sstyle\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
VAR_USE = re.compile(r"var\(\s*(--[\w-]+)")
VAR_CALL = re.compile(r"var\([^()]*\)")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.text.strip()}"


@dataclass(frozen=True)
class Chunk:
    """A piece of CSS with the line number where it starts in its file."""

    css: str
    first_line: int


def blank_comments(css: str) -> str:
    """Remove comments but keep line breaks, so line numbers stay right."""
    return COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), css)


def strip_vars(value: str) -> str:
    previous = None
    while previous != value:
        previous = value
        value = VAR_CALL.sub(" ", value)
    return value


def has_nonzero_length(value: str) -> bool:
    return any(float(m.group(1)) != 0 for m in LENGTH.finditer(value))


def chunks_of(path: Path, text: str) -> list[Chunk]:
    if path.suffix == ".css":
        return [Chunk(text, 1)]
    out: list[Chunk] = []
    for m in STYLE_BLOCK.finditer(text):
        out.append(Chunk(m.group(1), text.count("\n", 0, m.start(1)) + 1))
    for m in STYLE_ATTR.finditer(text):
        value = m.group(1) if m.group(1) is not None else m.group(2)
        out.append(Chunk(value, text.count("\n", 0, m.start()) + 1))
    return out


def declarations(chunk: Chunk) -> list[tuple[int, str, str]]:
    css = blank_comments(chunk.css)
    found: list[tuple[int, str, str]] = []
    for m in DECLARATION.finditer(css):
        line = chunk.first_line + css.count("\n", 0, m.start())
        found.append((line, m.group(1).lower(), m.group(2).strip()))
    return found


def check_declaration(
    rel: str, line: int, prop: str, value: str, defined: set[str]
) -> list[Finding]:
    out: list[Finding] = []
    text = f"{prop}: {value}"
    bare = strip_vars(re.sub(r"url\([^)]*\)", " ", value))
    if HEX.search(bare) or COLOUR_FUNC.search(bare):
        out.append(Finding(rel, line, "raw-colour", text))
    elif COLOUR_PROPS.match(prop):
        words = set(re.findall(r"[a-zA-Z]+", bare.lower()))
        if words & NAMED_COLOURS:
            out.append(Finding(rel, line, "raw-colour", text))
    if prop == "font-size":
        if has_nonzero_length(bare) or SIZE_WORDS.search(bare):
            out.append(Finding(rel, line, "raw-type", text))
    elif prop == "font-family":
        if bare.strip().lower() not in KEYWORDS:
            out.append(Finding(rel, line, "raw-type", text))
    elif prop == "font" and bare.strip().lower() not in KEYWORDS and bare.replace("/", " ").strip():
        out.append(Finding(rel, line, "raw-type", text))
    if prop.startswith("border") and prop.endswith("radius") and has_nonzero_length(bare):
        out.append(Finding(rel, line, "raw-radius", text))
    for name in VAR_USE.findall(value):
        if name not in defined:
            out.append(Finding(rel, line, "undefined-token", text))
    return out


def web_files(root: Path) -> list[Path]:
    base = root / WEB
    if not base.is_dir():
        return []
    files = [
        p
        for p in base.rglob("*")
        if p.suffix in {".css", ".html"}
        and p.is_file()
        and not any(part in SKIP_DIRS for part in p.relative_to(base).parts[:-1])
    ]
    return sorted(files)


def scan(root: Path) -> list[Finding]:
    files = web_files(root)
    tokens_path = root / "apps/web/assets/design-tokens.css"
    texts = {p: p.read_text(encoding="utf-8") for p in files}
    if tokens_path.is_file() and tokens_path not in texts:
        texts[tokens_path] = tokens_path.read_text(encoding="utf-8")
    defined: set[str] = set()
    for path, text in texts.items():
        for chunk in chunks_of(path, text):
            defined.update(re.findall(r"(--[\w-]+)\s*:", blank_comments(chunk.css)))
    findings: list[Finding] = []
    for path, text in texts.items():
        rel = path.relative_to(root).as_posix()
        if rel in EXEMPT:
            continue
        for number, source_line in enumerate(blank_comments(text).splitlines(), start=1):
            if EXTERNAL.search(source_line):
                findings.append(Finding(rel, number, "external-resource", source_line))
        for chunk in chunks_of(path, text):
            for line_no, prop, value in declarations(chunk):
                findings += check_declaration(rel, line_no, prop, value, defined)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check web screens for design token use.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args(argv)
    findings = scan(Path(args.root))
    for finding in findings:
        print(finding)
    if findings:
        print(f"\n{len(findings)} design token problem(s). See apps/web/assets/design-tokens.css.")
        return 1
    print("check_design_tokens: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
