"""The numbered chat the model reads, and the places in it that a quote can point to.

The numbered chat and the mapping both work from one ChatContext, so a message number from the
model always means the same message: every message is a line, including system lines, media
placeholders, deleted messages and voice notes (a voice note's line is its transcript text).
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass

from packages.contracts import Message, Transcript

from .rules import prompt_format

_LINE_BREAKS = re.compile(r"\s*[\r\n]+\s*")


@dataclass(frozen=True)
class VoiceEvidence:
    """The transcript of a voice note, found by the id of the message that carried it."""

    voice_note_id: str
    transcript: Transcript


@dataclass(frozen=True)
class ChatContext:
    """Everything the prompt was built from. Positions in `messages` are the model's numbers."""

    deal_id: str
    messages: tuple[Message, ...]
    participants: Mapping[str, str]
    voice: Mapping[str, VoiceEvidence]


def _flat(text: str) -> str:
    """One line per message, so line numbers stay message numbers."""
    return _LINE_BREAKS.sub(" ", text)


def _span_texts(evidence: VoiceEvidence) -> list[str]:
    return [_flat(span.text) for span in evidence.transcript.spans]


def line_text(chat: ChatContext, message: Message) -> str:
    evidence = chat.voice.get(message.id)
    if evidence is not None:
        return " ".join(_span_texts(evidence))
    return _flat(message.text)


def sender_label(chat: ChatContext, message: Message) -> str:
    """The sender name shown on the message's line; system lines and unknown senders get the
    configured system label."""
    if message.is_system:
        return prompt_format().system_sender
    return chat.participants.get(message.sender_id, prompt_format().system_sender)


def numbered_chat(chat: ChatContext) -> str:
    """The user message of the prompt: one `[n] sender: text` line per message, from 1."""
    fmt = prompt_format()
    lines = []
    for index, message in enumerate(chat.messages, start=1):
        sender = chat.participants.get(message.sender_id, fmt.system_sender)
        if message.is_system:
            sender = fmt.system_sender
        lines.append(
            fmt.message_format.format(index=index, sender=sender, text=line_text(chat, message))
        )
    return "\n".join(lines)


def locate_in_voice(evidence: VoiceEvidence, quote: str) -> tuple[int, int] | None:
    """Start and end in ms of the transcript spans that hold the quote, or None if not found.

    A quote inside one span gets that span's times; a quote across spans gets the first span's
    start and the last span's end.
    """
    if not quote:
        return None
    texts = _span_texts(evidence)
    joined = " ".join(texts)
    found = joined.find(quote)
    if found < 0:
        return None
    end = found + len(quote)
    first = last = None
    offset = 0
    for index, text in enumerate(texts):
        span_start, span_end = offset, offset + len(text)
        if span_start < end and span_end > found:
            first = index if first is None else first
            last = index
        offset = span_end + 1
    if first is None or last is None:
        return None
    spans = evidence.transcript.spans
    return spans[first].start_ms, spans[last].end_ms
