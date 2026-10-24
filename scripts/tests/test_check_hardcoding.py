"""Tests for scripts/check_hardcoding.py (written before the script)."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "check_hardcoding.py"
spec = importlib.util.spec_from_file_location("check_hardcoding", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rules(root: Path) -> set[str]:
    return {f.rule for f in mod.scan(root)}


def test_clean_repo_passes(tmp_path: Path) -> None:
    write(tmp_path, "packages/ingest/parse.py", "def parse(text: str) -> str:\n    return text\n")
    assert mod.scan(tmp_path) == []


@pytest.mark.parametrize(
    "line",
    [
        'VAULT = "/home/someone/vault"',
        "VAULT = '/Users/someone/vault'",
        'TMP = "/tmp/veridoc"',
        'WIN = "C:\\\\Users\\\\x"',
        'WIN2 = "D:/data"',
    ],
)
def test_absolute_paths_fail(tmp_path: Path, line: str) -> None:
    write(tmp_path, "packages/vault/store.py", line + "\n")
    assert rules(tmp_path) == {"absolute-path"}


@pytest.mark.parametrize(
    "line",
    [
        'URL = "http://localhost:8080/api"',
        'HOST = "127.0.0.1"',
        'URL = "http://0.0.0.0:9000"',
        "uvicorn.run(app, port=8000)",
        "const base = 'http://localhost/x';",
    ],
)
def test_localhost_and_ports_fail_outside_settings(tmp_path: Path, line: str) -> None:
    write(tmp_path, "apps/api/server.py", line + "\n")
    assert rules(tmp_path) == {"localhost-or-port"}


def test_localhost_and_ports_allowed_in_settings_module(tmp_path: Path) -> None:
    write(tmp_path, "apps/api/settings.py", 'host: str = "127.0.0.1"\nport: int = 8080\n')
    assert mod.scan(tmp_path) == []


def test_absolute_path_not_allowed_even_in_settings_module(tmp_path: Path) -> None:
    write(tmp_path, "apps/api/settings.py", 'home = "/home/someone"\n')
    assert rules(tmp_path) == {"absolute-path"}


@pytest.mark.parametrize(
    "line",
    [
        'if sender == "Raju":',
        'name = "Meena"',
        "price = 480",
        "advance = 48000",
        "advance = 48,000",
        "total = 96000",
        'when = "15 Nov"',
    ],
)
def test_sample_names_amounts_dates_fail_in_code(tmp_path: Path, line: str) -> None:
    write(tmp_path, "packages/intelligence/rules.py", line + "\n")
    assert rules(tmp_path) == {"sample-data"}


def test_sample_data_allowed_in_tests_and_fixtures(tmp_path: Path) -> None:
    write(tmp_path, "packages/ingest/tests/test_parse.py", 'assert sender == "Raju"\nprice = 480\n')
    write(tmp_path, "packages/ingest/fixtures/chat.json", '{"sender": "Meena", "text": "480"}')
    write(tmp_path, "eval/chats/chat1.txt", "Raju: 200 shirts at 480\n")
    write(tmp_path, "docs/PRD.md", "Raju and Meena, 48000\n")
    assert mod.scan(tmp_path) == []


def test_numbers_inside_css_units_and_words_are_not_flagged(tmp_path: Path) -> None:
    write(
        tmp_path,
        "apps/web/assets/app.css",
        ".a { max-width: 480px; color: #480; } .b { z-index: 4800; }\n",
    )
    assert mod.scan(tmp_path) == []


def test_stub_without_issue_fails(tmp_path: Path) -> None:
    write(tmp_path, "apps/api/routers/ingest.py", "# STUB: returns fixture\n")
    assert rules(tmp_path) == {"stub-marker"}


def test_stub_with_issue_passes(tmp_path: Path) -> None:
    write(tmp_path, "apps/api/routers/ingest.py", "# STUB: replaced by #14\n")
    assert mod.scan(tmp_path) == []


def test_js_stub_comment_with_issue_passes(tmp_path: Path) -> None:
    write(tmp_path, "apps/web/screens/s1-deals/app.js", "// STUB: replaced by #27\n")
    assert mod.scan(tmp_path) == []


def test_stub_in_tests_is_not_checked(tmp_path: Path) -> None:
    write(tmp_path, "packages/ingest/tests/test_x.py", "# STUB: anything goes here\n")
    assert mod.scan(tmp_path) == []


def test_line_with_ok_marker_is_skipped(tmp_path: Path) -> None:
    write(tmp_path, "apps/api/x.py", 'HOST = "127.0.0.1"  # hardcoding: ok (loopback guard)\n')
    assert mod.scan(tmp_path) == []


def test_findings_report_path_and_line(tmp_path: Path) -> None:
    write(tmp_path, "apps/api/x.py", 'ok = 1\nHOST = "127.0.0.1"\n')
    [finding] = mod.scan(tmp_path)
    assert finding.path == "apps/api/x.py"
    assert finding.line == 2


def test_main_returns_nonzero_on_findings(tmp_path: Path) -> None:
    write(tmp_path, "apps/api/x.py", 'HOST = "127.0.0.1"\n')
    assert mod.main(["--root", str(tmp_path)]) == 1
    write(tmp_path, "apps/api/x.py", "HOST = 1\n")
    assert mod.main(["--root", str(tmp_path)]) == 0


def test_the_real_repository_is_clean() -> None:
    assert mod.main(["--root", str(SCRIPT.parent.parent)]) == 0
