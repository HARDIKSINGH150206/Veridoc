import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "check_design_tokens.py"
spec = importlib.util.spec_from_file_location("check_design_tokens", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

TOKENS = (
    ":root { --color-text: #111111; --space-2: 0.5rem; --radius-md: 0.5rem;"
    " --font-size-sm: 0.875rem; }\n"
)


def make(root: Path, files: dict[str, str]) -> None:
    (root / "apps/web/assets").mkdir(parents=True, exist_ok=True)
    (root / "apps/web/assets/design-tokens.css").write_text(TOKENS, encoding="utf-8")
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def rules(root: Path) -> set[str]:
    return {f.rule for f in mod.scan(root)}


def test_screen_using_only_tokens_passes(tmp_path: Path) -> None:
    css = (
        ".a { color: var(--color-text); padding: var(--space-2); border-radius: var(--radius-md); }"
    )
    make(tmp_path, {"apps/web/screens/s1-deals/deals.css": css})
    assert mod.scan(tmp_path) == []


@pytest.mark.parametrize(
    "decl",
    [
        "color: #fff",
        "background: #1B2430",
        "border: 1px solid #c5cbd5",
        "color: rgb(10, 20, 30)",
        "background: rgba(0,0,0,.5)",
        "color: hsl(10 20% 30%)",
        "color: red",
        "background-color: White",
        "box-shadow: 0 1px 2px black",
        "fill: navy",
    ],
)
def test_raw_colours_fail(tmp_path: Path, decl: str) -> None:
    make(tmp_path, {"apps/web/screens/s1-deals/deals.css": f".a {{ {decl}; }}"})
    assert rules(tmp_path) == {"raw-colour"}


@pytest.mark.parametrize(
    "decl",
    [
        "color: transparent",
        "color: currentColor",
        "color: inherit",
        "background: none",
        "border: 1px solid var(--color-text)",
        "box-shadow: 0 1px 2px var(--color-text)",
    ],
)
def test_non_colour_keywords_and_tokens_pass(tmp_path: Path, decl: str) -> None:
    make(tmp_path, {"apps/web/screens/s1-deals/deals.css": f".a {{ {decl}; }}"})
    assert mod.scan(tmp_path) == []


def test_selectors_that_look_like_hex_are_not_colours(tmp_path: Path) -> None:
    make(tmp_path, {"apps/web/screens/s1-deals/deals.css": "#add, #bad { margin: 0; }"})
    assert mod.scan(tmp_path) == []


def test_raw_font_size_and_family_fail(tmp_path: Path) -> None:
    make(
        tmp_path,
        {
            "apps/web/a.css": ".a { font-size: 13px; }",
            "apps/web/b.css": ".b { font-family: Arial, sans-serif; }",
            "apps/web/c.css": ".c { font: 600 13px/1 system-ui; }",
        },
    )
    found = mod.scan(tmp_path)
    assert {(f.path, f.rule) for f in found} == {
        ("apps/web/a.css", "raw-type"),
        ("apps/web/b.css", "raw-type"),
        ("apps/web/c.css", "raw-type"),
    }


def test_font_size_tokens_and_inherit_pass(tmp_path: Path) -> None:
    make(
        tmp_path, {"apps/web/a.css": ".a { font-size: var(--font-size-sm); } .b { font: inherit; }"}
    )
    assert mod.scan(tmp_path) == []


def test_raw_radius_fails_but_zero_and_tokens_pass(tmp_path: Path) -> None:
    make(tmp_path, {"apps/web/a.css": ".a { border-radius: 6px; }"})
    assert rules(tmp_path) == {"raw-radius"}
    make(
        tmp_path,
        {"apps/web/a.css": ".a { border-radius: 0; } .b { border-radius: var(--radius-md); }"},
    )
    assert mod.scan(tmp_path) == []


def test_undefined_token_fails_and_local_custom_property_passes(tmp_path: Path) -> None:
    make(tmp_path, {"apps/web/a.css": ".a { color: var(--no-such-token); }"})
    assert rules(tmp_path) == {"undefined-token"}
    make(tmp_path, {"apps/web/a.css": ".a { --bar: 40%; width: var(--bar); }"})
    assert mod.scan(tmp_path) == []


def test_html_style_blocks_and_attributes_are_checked(tmp_path: Path) -> None:
    html = '<style>.a { color: #fff; }</style><div style="background: #000">x</div>'
    make(tmp_path, {"apps/web/screens/s1-deals/index.html": html})
    found = mod.scan(tmp_path)
    assert len(found) == 2 and {f.rule for f in found} == {"raw-colour"}


def test_cdn_and_external_resources_fail(tmp_path: Path) -> None:
    make(
        tmp_path,
        {
            "apps/web/a.css": "@import url('https://fonts.example.org/x.css');",
            "apps/web/b.html": '<script src="https://cdn.example.org/x.js"></script>',
            "apps/web/c.css": ".a { background: url(//cdn.example.org/x.png); }",
        },
    )
    found = mod.scan(tmp_path)
    assert {f.rule for f in found} == {"external-resource"}
    assert len(found) == 3


def test_local_resources_pass(tmp_path: Path) -> None:
    make(tmp_path, {"apps/web/a.css": "@font-face { src: url('fonts/x.woff2'); }"})
    assert mod.scan(tmp_path) == []


def test_tokens_fonts_and_font_files_are_exempt(tmp_path: Path) -> None:
    make(
        tmp_path,
        {"apps/web/assets/fonts.css": "@font-face { font-family: 'X'; src: url('f/x.woff2'); }"},
    )
    assert mod.scan(tmp_path) == []


def test_tests_folders_are_not_scanned(tmp_path: Path) -> None:
    make(tmp_path, {"apps/web/tests/sample.css": ".a { color: #fff; }"})
    assert mod.scan(tmp_path) == []


def test_findings_carry_path_and_line(tmp_path: Path) -> None:
    make(tmp_path, {"apps/web/a.css": ".x { margin: 0; }\n.a { color: #fff; }\n"})
    [finding] = mod.scan(tmp_path)
    assert (finding.path, finding.line) == ("apps/web/a.css", 2)


def test_main_exit_codes(tmp_path: Path) -> None:
    make(tmp_path, {"apps/web/a.css": ".a { color: #fff; }"})
    assert mod.main(["--root", str(tmp_path)]) == 1
    make(tmp_path, {"apps/web/a.css": ".a { color: var(--color-text); }"})
    assert mod.main(["--root", str(tmp_path)]) == 0


def test_the_real_repository_is_clean() -> None:
    assert mod.main(["--root", str(SCRIPT.parent.parent)]) == 0
