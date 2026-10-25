"""Demo recap with an echo code for the walking skeleton (issue #29). Pure: no I/O, no clock.

The wording here is a stand-in. The real recap is built from the playbook's per-language templates
(playbooks/templates/, issue #64) and only from confirmed terms. The hashing follows
docs/INTEGRITY_SPEC.md section 7: hash the recap content WITHOUT the code line, derive the code
from that hash, then attach the code line to make the text that is sent.
"""

import json
import uuid
from collections.abc import Sequence

from pydantic import ValidationError

from packages.contracts import (
    AgreedTerm,
    DateValue,
    DurationValue,
    EchoCode,
    EventValue,
    Language,
    MessageSourceRef,
    MoneyValue,
    PartialDateValue,
    QuantityValue,
    Recap,
    RecapLine,
    TermValue,
    TextValue,
    Timestamp,
    VoiceSourceRef,
)
from packages.ingest.samples import Sample
from packages.integrity import JsonValue, derive_echo_code, recap_hash, to_hex

_NAMESPACE = uuid.UUID("c3b6a8f2-5d1e-4f7a-8e29-1a4d7b0c6e53")
_PAISE_PER_RUPEE = 100


class ConfirmationRequired(ValueError):
    """A recap is built only from confirmed terms, and there are none."""


class InvalidConfirmation(ValueError):
    """Confirmed terms that do not belong to the sample or were not confirmed by its user."""


def parse_confirmed_terms(payload: object) -> list[AgreedTerm]:
    """Read `{"terms": [AgreedTerm, ...]}` as sent by the screen, with the strict contract models.

    The details of a failure are not repeated, because they may contain chat content.
    """
    if not isinstance(payload, dict) or set(payload) != {"terms"}:
        raise InvalidConfirmation("the body must be an object with a terms list")
    items = payload["terms"]
    if not isinstance(items, list):
        raise InvalidConfirmation("terms must be a list")
    try:
        return [AgreedTerm.model_validate_json(json.dumps(item)) for item in items]
    except (ValidationError, ValueError):
        raise InvalidConfirmation("a term is not a confirmed term") from None


def check_confirmed_terms(sample: Sample, terms: Sequence[AgreedTerm]) -> None:
    """Terms must be confirmed by the sample's primary user, cite its messages and be unique."""
    if not terms:
        raise ConfirmationRequired("at least one confirmed term is needed")
    me = {p.id for p in sample.participants if p.is_me}
    message_ids = {m.id for m in sample.messages}
    if len({t.key for t in terms}) != len(terms):
        raise InvalidConfirmation("a term key appears twice")
    for term in terms:
        if term.confirmed_by not in me:
            raise InvalidConfirmation("a term was not confirmed by the primary user")
        for source in term.sources:
            if isinstance(source, MessageSourceRef) and source.message_id not in message_ids:
                raise InvalidConfirmation("a source is not a message of this sample")
            if isinstance(source, VoiceSourceRef):
                raise InvalidConfirmation("voice sources are not part of the sample")


def _render(value: TermValue) -> str:
    # STUB: replaced by #64 (per-language recap templates).
    match value:
        case MoneyValue(paise=paise):
            rupees, rest = divmod(int(paise), _PAISE_PER_RUPEE)
            return f"Rs {rupees}" if rest == 0 else f"Rs {rupees}.{rest:02d}"
        case QuantityValue(amount=amount, unit=unit):
            return amount if unit is None else f"{amount} {unit}"
        case DateValue(date=date):
            return date
        case PartialDateValue(month_day=month_day):
            return month_day
        case EventValue(event=event):
            return event.replace("_", " ")
        case DurationValue(amount=amount, unit=unit):
            return f"{amount} {unit.value}"
        case TextValue(text=text):
            return text
    raise AssertionError("unreachable: every TermValue is handled")  # pragma: no cover


def build_demo_recap(
    deal_id: str, version_n: int, terms: Sequence[AgreedTerm], created_at: Timestamp
) -> Recap:
    """The recap of one agreement version with its echo code, from confirmed terms only."""
    if not terms:
        raise ConfirmationRequired("a recap needs at least one confirmed term")
    # STUB: replaced by #64 (per-language recap templates).
    lines = tuple(
        RecapLine(
            term_key=term.key,
            text=f"{term.key.replace('_', ' ')}: {_render(term.value)}",
            sources=term.sources,
        )
        for term in sorted(terms, key=lambda t: t.key)
    )
    body_text = "\n".join(line.text for line in lines)
    content: dict[str, JsonValue] = {
        "deal_id": deal_id,
        "version_n": version_n,
        "language": Language.EN.value,
        "lines": [line.model_dump(mode="json") for line in lines],
        "body_text": body_text,
    }
    digest = recap_hash(content)
    code = derive_echo_code(digest)
    return Recap(
        id=str(uuid.uuid5(_NAMESPACE, f"{deal_id}:{version_n}")),
        deal_id=deal_id,
        version_n=version_n,
        language=Language.EN,
        lines=lines,
        body_text=body_text,
        text=f"{body_text}\nIf all correct, reply: CONFIRM {code}",
        recap_hash=to_hex(digest),
        echo_code=EchoCode(code=code, recap_hash=to_hex(digest), version_n=version_n),
        created_at=created_at,
    )
