"""Read bundled demo messages without parsing user input or writing records."""

import json
from pathlib import Path

from pydantic import ValidationError

from packages.contracts import Message


class SampleNotFound(Exception):
    """The requested name is not a bundled sample."""


class SampleUnavailable(Exception):
    """Bundled data does not match the shared contract."""


def load_messages(sample_id: str, directory: Path) -> list[Message]:
    """Validate a bundled array with the actual shared contract, never a local copy."""
    candidates = {path.stem: path for path in directory.glob("*.json") if not path.is_symlink()}
    if sample_id not in candidates:
        raise SampleNotFound
    try:
        payload = json.loads(candidates[sample_id].read_text(encoding="utf-8"))
        if not isinstance(payload, list) or not payload:
            raise ValueError
        return [Message.model_validate_json(json.dumps(item)) for item in payload]
    except (OSError, ValueError, ValidationError):
        raise SampleUnavailable("Sample data unavailable") from None
