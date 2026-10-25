"""Read bundled demo messages without parsing user input or writing records."""

import json
from importlib import import_module
from pathlib import Path

from pydantic import BaseModel, ValidationError


class SampleNotFound(Exception):
    """The requested name is not a bundled sample."""


class SampleUnavailable(Exception):
    """Bundled data or its shared contract is unavailable."""


def load_messages(sample_id: str, directory: Path) -> list[BaseModel]:
    """Validate a bundled array with the actual shared contract, never a local copy."""
    candidates = {path.stem: path for path in directory.glob("*.json") if not path.is_symlink()}
    if sample_id not in candidates:
        raise SampleNotFound
    try:
        # Resolve lazily so dev still boots before contracts PR #40 is merged.
        model = import_module("packages.contracts.chat").Message
        if not isinstance(model, type) or not issubclass(model, BaseModel):
            raise TypeError
        payload = json.loads(candidates[sample_id].read_text(encoding="utf-8"))
        if not isinstance(payload, list) or not payload:
            raise ValueError
        return [model.model_validate_json(json.dumps(item)) for item in payload]
    except (ImportError, AttributeError, OSError, ValueError, TypeError, ValidationError):
        raise SampleUnavailable("Sample data unavailable") from None
