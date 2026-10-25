"""Map the local model's output to contract Terms (issues #63 and #64, Q-64).

Rules that always hold: every term is proposed by the AI (origin ai), is never confirmed here, and
a term that does not fit becomes an unclear term marked needs_review with no value, never an
exception. Values are never changed: a value that disagrees with its own quote is flagged for a
person to check. Nothing here touches the vault or the hash path.
"""

import re
import uuid
from decimal import Decimal, InvalidOperation

from pydantic import ValidationError

from packages.contracts import (
    Confidence,
    EventValue,
    MessageSourceRef,
    MoneyValue,
    PartialDateValue,
    QuantityValue,
    SourceRef,
    Term,
    TermOrigin,
    TermState,
    TermValue,
    TextValue,
    VoiceSourceRef,
)

from .chat import ChatContext, line_text, locate_in_voice, sender_label
from .output import MalformedTerm, ModelOutput, TermOutput
from .rules import TermRules, term_rules

_ID_NAMESPACE = uuid.UUID("6f1d2b5c-3a8e-4c47-9b0e-7d5a1c2e8f40")
_MM_DD = re.compile(r"[0-9]{2}-[0-9]{2}")
_NUMBER = re.compile(r"[0-9][0-9,]*(?:\.[0-9]+)?")
_PAISE_PER_RUPEE = 100


def map_output(output: ModelOutput, chat: ChatContext) -> list[Term]:
    """One Term per entry of the model's output, in the model's order. Never raises on bad terms."""
    rules = term_rules()
    return [_map_term(key, raw, chat, rules) for key, raw in output.terms.items()]


def _term_id(chat: ChatContext, key: str) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, f"{chat.deal_id}:{key}"))


def _numbers(quotes: list[str]) -> set[Decimal]:
    found: set[Decimal] = set()
    for quote in quotes:
        for text in _NUMBER.findall(quote):
            try:
                found.add(Decimal(text.replace(",", "")))
            except InvalidOperation:  # pragma: no cover - the pattern only matches numbers
                continue
    return found


def _typed_value(kind: str, value: object, rules: TermRules) -> TermValue | None:
    """The contract value for the model's value, or None if it does not fit the term's kind."""
    if isinstance(value, bool):
        return None
    if kind in {"money", "quantity"}:
        if not isinstance(value, int) or value < 0:
            return None
        if kind == "money":
            return MoneyValue(kind="money", paise=str(value * _PAISE_PER_RUPEE))
        return QuantityValue(kind="quantity", amount=str(value), unit=None)
    if not isinstance(value, str):
        return None
    if kind == "date":
        if _MM_DD.fullmatch(value):
            try:
                return PartialDateValue(kind="partial_date", month_day=f"--{value}")
            except ValidationError:
                return None
        if value in rules.events:
            return EventValue(kind="event", event=value)
        return None
    return TextValue(kind="text", text=value) if value.strip() else None


def _sources(raw: TermOutput, chat: ChatContext) -> tuple[list[SourceRef], bool]:
    """Sources from the model's message numbers and quotes, and whether all of them held up."""
    sources: list[SourceRef] = []
    sound = len(raw.quote) == len(raw.msg)
    for index, position in enumerate(raw.msg):
        quote = raw.quote[index] if index < len(raw.quote) else None
        if not 1 <= position <= len(chat.messages):
            sound = False
            continue
        message = chat.messages[position - 1]
        # The model reads "[n] sender: text", so a party term may quote the sender's name.
        in_text = quote is not None and quote != "" and quote in line_text(chat, message)
        grounded = in_text or (
            quote is not None and quote != "" and quote in sender_label(chat, message)
        )
        source: SourceRef
        evidence = chat.voice.get(message.id)
        located = locate_in_voice(evidence, quote) if evidence and in_text and quote else None
        if evidence is not None and located is not None and quote is not None:
            source = VoiceSourceRef(
                kind="voice",
                voice_note_id=evidence.voice_note_id,
                start_ms=located[0],
                end_ms=located[1],
                quote=quote,
            )
        else:
            sound = sound and grounded and evidence is None
            source = MessageSourceRef(
                kind="message", message_id=message.id, quote=quote if in_text else None
            )
        if source not in sources:
            sources.append(source)
    return sources, sound


def _original_wording(raw: TermOutput) -> str | None:
    return " / ".join(raw.quote) if raw.quote else None


def _review_term(key: str, chat: ChatContext, raw: str | None, sources: list[SourceRef]) -> Term:
    return _build(key, chat, TermState.UNCLEAR, None, raw, None, sources, review=True)


def _build(
    key: str,
    chat: ChatContext,
    state: TermState,
    value: TermValue | None,
    raw: str | None,
    reason: str | None,
    sources: list[SourceRef],
    *,
    review: bool,
) -> Term:
    return Term(
        id=_term_id(chat, key),
        deal_id=chat.deal_id,
        key=key,
        value=value,
        raw=raw,
        state=state,
        unclear_reason=reason,
        origin=TermOrigin.AI,
        confidence=Confidence.LOW if review else Confidence.MEDIUM,
        needs_review=review,
        sources=sources,
        alternatives=[],
        confirmed_at=None,
        confirmed_by=None,
        acknowledged_by_other=False,
    )


def _map_term(
    key: str, raw: TermOutput | MalformedTerm, chat: ChatContext, rules: TermRules
) -> Term:
    if isinstance(raw, MalformedTerm):
        return _review_term(key, chat, raw.raw, [])
    try:
        state = TermState(raw.status)
    except ValueError:
        sources, _ = _sources(raw, chat)
        shown = _original_wording(raw) or raw.model_dump_json(exclude_defaults=True)
        return _review_term(key, chat, shown, sources)
    if state is TermState.MISSING:
        return _build(key, chat, state, None, None, None, [], review=False)

    kind = rules.kind_of(key)
    sources, sound = _sources(raw, chat)
    wording = _original_wording(raw)
    review = not sound
    value: TermValue | None = None
    reason: str | None = None

    if state is TermState.STATED:
        value = _typed_value(kind, raw.value, rules)
        if value is None:
            return _review_term(
                key, chat, wording or raw.model_dump_json(exclude_defaults=True), sources
            )
        review = review or not sources
        if kind in {"money", "quantity"} and isinstance(raw.value, int):
            numbers = _numbers(raw.quote)
            review = review or (bool(numbers) and Decimal(raw.value) not in numbers)
    elif state is TermState.UNCLEAR:
        reason = raw.reason
        review = review or raw.value is not None
        review = review or (reason is not None and reason not in rules.unclear_reasons)
        review = review or (kind == "money" and bool(_numbers(raw.quote)))
    else:
        review = review or len(sources) < 2 or raw.value is not None
    return _build(key, chat, state, value, wording, reason, sources, review=review)
