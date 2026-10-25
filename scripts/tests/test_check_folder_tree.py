import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "scripts" / "check_folder_tree.py"


def test_every_file_read_names_its_encoding() -> None:
    """The docs hold box-drawing characters (the ARCHITECTURE tree). Without an explicit encoding,
    Windows decodes them as cp1252 and the check fails on a correct repository."""
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    missing = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"read_text", "open"}
        and not any(keyword.arg == "encoding" for keyword in node.keywords)
    ]
    assert missing == [], f"file reads without encoding= on lines {missing}"


def test_passes_on_the_repository_without_utf8_mode() -> None:
    """Run as a Windows user would: UTF-8 mode off, so the locale encoding is the default."""
    env = {**os.environ, "PYTHONUTF8": "0"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip().endswith("OK")
