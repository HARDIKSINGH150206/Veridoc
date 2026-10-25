"""Read bundled demo samples without parsing user input or writing records."""

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from packages.contracts import Message, Participant


class SampleNotFound(Exception):
    """The requested name is not a bundled sample."""


class SampleUnavailable(Exception):
    """Bundled data does not match the shared contract."""


class SampleMeta(BaseModel):
    """Who is in a bundled sample and which playbook it follows."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    playbook_id: str
    participants: tuple[Participant, ...]


@dataclass(frozen=True)
class Sample:
    playbook_id: str
    participants: tuple[Participant, ...]
    messages: tuple[Message, ...]


def _candidates(directory: Path) -> dict[str, Path]:
    return {path.stem: path for path in directory.glob("*.json") if not path.is_symlink()}


def list_samples(fixtures: Path) -> list[str]:
    """Names of the bundled samples, sorted."""
    return sorted(_candidates(fixtures / "messages"))


def load_messages(sample_id: str, directory: Path) -> list[Message]:
    """Validate a bundled array with the actual shared contract, never a local copy."""
    candidates = _candidates(directory)
    if sample_id not in candidates:
        raise SampleNotFound
    try:
        payload = json.loads(candidates[sample_id].read_text(encoding="utf-8"))
        if not isinstance(payload, list) or not payload:
            raise ValueError
        return [Message.model_validate_json(json.dumps(item)) for item in payload]
    except (OSError, ValueError, ValidationError):
        raise SampleUnavailable("Sample data unavailable") from None


def load_sample(sample_id: str, fixtures: Path) -> Sample:
    """Messages, participants and playbook of one bundled sample. Fails closed."""
    messages = load_messages(sample_id, fixtures / "messages")
    try:
        meta = SampleMeta.model_validate_json(
            (fixtures / "meta" / f"{sample_id}.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError, ValidationError):
        raise SampleUnavailable("Sample data unavailable") from None
    known = {p.id for p in meta.participants}
    if not {m.sender_id for m in messages} <= known:
        raise SampleUnavailable("Sample data unavailable")
    return Sample(meta.playbook_id, meta.participants, tuple(messages))
