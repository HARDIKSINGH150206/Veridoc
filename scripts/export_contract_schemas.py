"""Export JSON Schema for every contract model.

Writes one <Model>.schema.json per model plus index.json (contracts version and the
requirement IDs each model serves) into a git-ignored folder, so the frontend and other tools can
read the shapes without importing Python.

Run: python scripts/export_contract_schemas.py [--out FOLDER]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pydantic import TypeAdapter  # noqa: E402

from packages.contracts import ALL_MODELS, CONTRACTS_VERSION, SourceRef  # noqa: E402

DEFAULT_OUT = "out/contract-schemas"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export JSON Schema for the contract models.")
    parser.add_argument("--out", default=str(ROOT / DEFAULT_OUT), help="output folder")
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    index: dict[str, dict[str, Any]] = {}
    for model in ALL_MODELS:
        schema = model.model_json_schema()
        write_json(out / f"{model.__name__}.schema.json", schema)
        index[model.__name__] = {"requirements": schema.get("requirements", [])}
    # SourceRef is a union of two models, so it is exported through a TypeAdapter.
    source_ref_schema = TypeAdapter(SourceRef).json_schema()
    write_json(out / "SourceRef.schema.json", source_ref_schema)
    index["SourceRef"] = {"requirements": ["FR-EXT-002", "FR-PLM-001"]}

    write_json(out / "index.json", {"contracts_version": CONTRACTS_VERSION, "models": index})
    print(f"wrote {len(index)} schemas to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
