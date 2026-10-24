import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "export_contract_schemas.py"
spec = importlib.util.spec_from_file_location("export_contract_schemas", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_exports_one_schema_per_model_and_an_index(tmp_path: Path) -> None:
    assert mod.main(["--out", str(tmp_path)]) == 0
    names = {p.name for p in tmp_path.glob("*.schema.json")}
    assert "Message.schema.json" in names
    assert "Receipt.schema.json" in names
    assert "SourceRef.schema.json" in names
    index = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    assert index["contracts_version"] == "0.1.0"
    assert "Term" in index["models"]
    assert index["models"]["Term"]["requirements"]
    term = json.loads((tmp_path / "Term.schema.json").read_text(encoding="utf-8"))
    assert term["title"] == "Term"
    assert "properties" in term


def test_default_output_folder_is_git_ignored() -> None:
    root = SCRIPT.parent.parent
    default = (root / mod.DEFAULT_OUT).as_posix() + "/"
    ignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert mod.DEFAULT_OUT.split("/")[0] + "/" in ignore.splitlines()
    assert default
