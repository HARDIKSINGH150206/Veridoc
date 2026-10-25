"""Builders for chats used by the model adapter tests (synthetic data only)."""

import uuid
from datetime import datetime, timedelta, timezone

from packages.contracts import Language, Message, MessageOrigin, Transcript, TranscriptSpan
from packages.intelligence.model_adapter import ChatContext, VoiceEvidence

NAMESPACE = uuid.UUID("0b7f4f1e-6d6c-4c0e-8a53-5f1f3f0c9a11")
DEAL_ID = str(uuid.uuid5(NAMESPACE, "deal"))
SYSTEM_SENDER_ID = str(uuid.uuid5(NAMESPACE, "system"))
START = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone(timedelta(minutes=330)))


def uid(label: str) -> str:
    return str(uuid.uuid5(NAMESPACE, label))


class ChatBuilder:
    """Adds messages in order. Positions are 1-based, as in the numbered chat."""

    def __init__(self) -> None:
        self.messages: list[Message] = []
        self.names: dict[str, str] = {}
        self.voice: dict[str, VoiceEvidence] = {}

    def say(
        self, name: str, text: str, *, system: bool = False, attachment: str | None = None
    ) -> Message:
        seq = len(self.messages) + 1
        sender_id = SYSTEM_SENDER_ID if system else uid(f"participant:{name}")
        if not system:
            self.names[sender_id] = name
        message = Message(
            id=uid(f"message:{seq}"),
            deal_id=DEAL_ID,
            seq=seq,
            sender_id=sender_id,
            ts=START + timedelta(minutes=seq),
            text=text,
            attachment_hash=attachment,
            is_system=system,
            origin=MessageOrigin.EXPORT,
        )
        self.messages.append(message)
        return message

    def voice_note(self, name: str, spans: list[tuple[int, int, str]]) -> Message:
        message = self.say(name, "<attached: voice.opus>", attachment="a" * 64)
        transcript = Transcript(
            id=uid(f"transcript:{message.seq}"),
            voice_note_id=uid(f"voice:{message.seq}"),
            model="test-speech",
            model_version="0",
            language=Language.EN,
            spans=tuple(
                TranscriptSpan(start_ms=a, end_ms=b, text=t, confidence=0.9) for a, b, t in spans
            ),
            supersedes_id=None,
            created_at=START,
        )
        self.voice[message.id] = VoiceEvidence(
            voice_note_id=transcript.voice_note_id, transcript=transcript
        )
        return message

    def context(self) -> ChatContext:
        return ChatContext(
            deal_id=DEAL_ID,
            messages=tuple(self.messages),
            participants=dict(self.names),
            voice=dict(self.voice),
        )
