"""The model adapter interface, a fake that replays recorded outputs, and the mode switch.

`local` is not built yet. The adapter returns a ModelOutput and nothing else: it never writes to
the vault or the hash path (ARCHITECTURE: the AI layer cannot reach them).
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, ValidationError

from .output import ModelOutput


@runtime_checkable
class ModelAdapter(Protocol):
    """Reads a numbered chat for one playbook and returns the model's JSON as ModelOutput."""

    def extract(self, numbered_chat: str, playbook_id: str) -> ModelOutput: ...


class UnrecordedChat(LookupError):
    """The fake adapter has no recording for this chat and playbook."""


class Recording(BaseModel):
    """One recorded model reply: the exact numbered chat it was given and what it returned."""

    model_config = ConfigDict(frozen=True)

    playbook_id: str
    numbered_chat: str
    output: ModelOutput


def load_recordings(directory: Path) -> tuple[Recording, ...]:
    """Read every *.json recording in a folder. A bad file is reported by name only."""
    recordings = []
    for path in sorted(directory.glob("*.json")):
        try:
            recordings.append(Recording.model_validate_json(path.read_text(encoding="utf-8")))
        except (ValidationError, OSError):
            raise ValueError(f"{path.name}: not a valid recording") from None
    return tuple(recordings)


class FakeModelAdapter:
    """Returns recorded outputs, including the model's known real mistakes. For tests and demos."""

    def __init__(self, recordings: Iterable[Recording]) -> None:
        self._recordings = {(r.playbook_id, r.numbered_chat): r.output for r in recordings}

    def extract(self, numbered_chat: str, playbook_id: str) -> ModelOutput:
        try:
            return self._recordings[(playbook_id, numbered_chat)]
        except KeyError:
            raise UnrecordedChat("no recording for this chat and playbook") from None


class LocalModelAdapter:
    """Will call the local model through llama-server. Not built yet."""

    def extract(self, numbered_chat: str, playbook_id: str) -> ModelOutput:
        # STUB: replaced by #69
        raise NotImplementedError(
            "VERIDOC_MODEL_MODE=local is not built yet (issue #69); use VERIDOC_MODEL_MODE=fake"
        )


def build_adapter(mode: str, recordings_dir: Path) -> ModelAdapter:
    """The adapter for VERIDOC_MODEL_MODE: fake or local."""
    if mode == "fake":
        return FakeModelAdapter(load_recordings(recordings_dir))
    if mode == "local":
        return LocalModelAdapter()
    raise ValueError(f"unknown model mode: {mode}")
