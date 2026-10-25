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
from typing import Any, get_args

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pydantic import TypeAdapter  # noqa: E402

from packages.contracts import ALL_MODELS, CONTRACTS_VERSION, UNION_TYPES  # noqa: E402

DEFAULT_OUT = "out/contract-schemas"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def union_requirements(union: Any) -> set[str]:
    """Requirement IDs of every model inside an Annotated union."""
    ids: set[str] = set()
    for member in get_args(get_args(union)[0]):
        extra = member.model_config.get("json_schema_extra")
        if isinstance(extra, dict):
            ids.update(str(r) for r in extra.get("requirements", []))
    return ids


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
    # The discriminated unions are not model classes, so they go through a TypeAdapter. Their
    # requirement IDs are those of the models they combine.
    for name, union in UNION_TYPES.items():
        write_json(out / f"{name}.schema.json", TypeAdapter(union).json_schema())
        index[name] = {"requirements": sorted(union_requirements(union))}

    write_json(out / "index.json", {"contracts_version": CONTRACTS_VERSION, "models": index})
    print(f"wrote {len(index)} schemas to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
