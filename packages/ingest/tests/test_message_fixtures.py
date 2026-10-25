"""Parsed synthetic exports for #13 (FR-IMP-001, FR-IMP-007)."""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest

from packages.contracts import Message

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
SAMPLES = ("clean", "ambiguous", "contradictory")


@pytest.mark.parametrize("sample", SAMPLES)
def test_parsed_messages_preserve_export(sample: str) -> None:
    messages = json.loads((FIXTURES / "messages" / f"{sample}.json").read_text("utf-8"))
    lines = (FIXTURES / f"{sample}.txt").read_text("utf-8").splitlines()
    assert len(messages) == len(lines)
    assert len({message["id"] for message in messages}) == len(messages)
    assert len({message["deal_id"] for message in messages}) == 1
    senders: dict[str, str] = {}
    for seq, (message, line) in enumerate(zip(messages, lines, strict=True), 1):
        timestamp, content = line.split(" - ", 1)
        sender, text = content.split(": ", 1)
        assert message["seq"] == seq
        senders.setdefault(sender, message["sender_id"])
        assert message["sender_id"] == senders[sender]
        assert message["text"] == text
        assert message["origin"] == "export"
        assert message["is_system"] is False
        parsed = datetime.fromisoformat(message["ts"])
        assert parsed.strftime("%d/%m/%Y, %H:%M") == timestamp
        assert parsed.utcoffset() is not None
        if text.startswith("<attached: "):
            audio = FIXTURES / text.removeprefix("<attached: ").removesuffix(">")
            assert message["attachment_hash"] == hashlib.sha256(audio.read_bytes()).hexdigest()
        else:
            assert message["attachment_hash"] is None
    assert len(set(senders.values())) == len(senders)


@pytest.mark.parametrize("sample", SAMPLES)
def test_every_message_validates_against_shared_contract(sample: str) -> None:
    messages = json.loads((FIXTURES / "messages" / f"{sample}.json").read_text("utf-8"))
    assert messages
    for message in messages:
        validated = Message.model_validate_json(json.dumps(message))
        assert validated.model_dump(mode="json") == message
