"""Fail the build when configuration or sample data is hardcoded in code.

Rules (see CLAUDE.md, section "No hardcoding"):
  absolute-path      absolute paths in string literals (everywhere in code, even in settings)
  localhost-or-port  localhost URLs, loopback addresses or ports outside the settings module
  sample-data        sample names, amounts or dates (Raju, Meena, 480, 48000 ...) outside tests,
                     fixtures, eval data and docs
  stub-marker        a STUB marker without "replaced by #<issue number>"

A line can opt out with a comment containing "hardcoding: ok (<reason>)".
Run: python scripts/check_hardcoding.py [--root PATH]. Exit code 1 if anything is found.
"""

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SETTINGS_MODULE = "apps/api/settings.py"
CODE_SUFFIXES = {".py", ".js", ".mjs", ".ts", ".html", ".css"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache"}
SKIP_DIRS |= {".pytest_cache", "docs", "eval", "test-vectors", "tests", "fixtures", "models"}
SELF = "scripts/check_hardcoding.py"

ABSOLUTE_PATH = re.compile(
    r"""(["'`])(?:/(?:home|Users|tmp|var|etc|usr|opt|mnt|root|srv)/|[A-Za-z]:[\\/]|file:///)"""
)
LOCALHOST = re.compile(r"localhost|127\.0\.0\.\d+|0\.0\.0\.0|\[::1\]", re.IGNORECASE)
PORT = re.compile(r"\bport\s*[=:]\s*\d{2,5}\b", re.IGNORECASE)
SAMPLE_NAMES = re.compile(
    r"\b(Raju|Meena|Kiran Design|Studio Nova|Patel Hardware|Sai Contractors"
    r"|Anita Sharma|Rohit Printers)\b"
)
SAMPLE_AMOUNTS = re.compile(
    r"(?<![\w#.\-])(?:480|48,000|48000|96,000|96000)(?![\w,.]*\d)(?!\s*(?:px|em|rem|vh|vw|ms|pt|%))"
)
SAMPLE_DATES = re.compile(r"\b(?:15|22) Nov\b")
STUB = re.compile(r"\bSTUB\b")
STUB_OK = re.compile(r"\bSTUB: replaced by #\d+")
OPT_OUT = re.compile(r"hardcoding: ok \(.+\)")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.text.strip()}"


def iter_code_files(root: Path) -> list[Path]:
    """Code files to check: tracked and untracked-but-not-ignored (git), else a directory walk."""
    out: list[Path] = []
    try:
        listing = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        candidates = [root / name for name in listing if (root / name).is_file()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        candidates = []
    if not candidates:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            candidates += [Path(dirpath) / f for f in filenames]
    for path in candidates:
        rel = path.relative_to(root)
        if path.suffix not in CODE_SUFFIXES:
            continue
        if rel.as_posix() == SELF or any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        out.append(path)
    return sorted(out)


def check_line(rel: str, number: int, line: str) -> list[Finding]:
    if OPT_OUT.search(line):
        return []
    found: list[Finding] = []
    is_settings = rel == SETTINGS_MODULE
    if ABSOLUTE_PATH.search(line):
        found.append(Finding(rel, number, "absolute-path", line))
    if not is_settings and (LOCALHOST.search(line) or PORT.search(line)):
        found.append(Finding(rel, number, "localhost-or-port", line))
    if SAMPLE_NAMES.search(line) or SAMPLE_AMOUNTS.search(line) or SAMPLE_DATES.search(line):
        found.append(Finding(rel, number, "sample-data", line))
    if STUB.search(line) and not STUB_OK.search(line):
        found.append(Finding(rel, number, "stub-marker", line))
    return found


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_code_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            findings += check_line(rel, number, line)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args(argv)
    findings = scan(Path(args.root))
    for finding in findings:
        print(finding)
    if findings:
        print(f"\n{len(findings)} hardcoding problem(s). See CLAUDE.md, section No hardcoding.")
        return 1
    print("check_hardcoding: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
