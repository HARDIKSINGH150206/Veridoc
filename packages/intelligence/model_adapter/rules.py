"""Adapter data read from model_adapter/data/: prompt wording and term typing.

These are the model's own conventions (LLM_HANDOVER.md section 5), kept as data so the playbook
alignment (Q-62) changes a file, not code.
"""

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class PromptFormat:
    message_format: str
    system_sender: str


@dataclass(frozen=True)
class TermRules:
    kinds: dict[str, str]
    default_kind: str
    unclear_reasons: frozenset[str]
    events: frozenset[str]

    def kind_of(self, key: str) -> str:
        return self.kinds.get(key, self.default_kind)


def _load(name: str) -> dict[str, object]:
    data: dict[str, object] = json.loads((DATA / name).read_text(encoding="utf-8"))
    return data


@cache
def prompt_format() -> PromptFormat:
    data = _load("prompt_format.json")
    return PromptFormat(str(data["message_format"]), str(data["system_sender"]))


@cache
def term_rules() -> TermRules:
    data = _load("term_rules.json")
    kinds = data["kinds"]
    reasons = data["unclear_reasons"]
    events = data["events"]
    assert isinstance(kinds, dict) and isinstance(reasons, list) and isinstance(events, list)
    return TermRules(
        kinds={str(k): str(v) for k, v in kinds.items()},
        default_kind=str(data["default_kind"]),
        unclear_reasons=frozenset(str(r) for r in reasons),
        events=frozenset(str(e) for e in events),
    )
