"""Shared enums, constrained types, typed term values and small models used by several contracts."""

import datetime as dt
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, Field, StringConstraints, model_validator

from .base import FrozenContractModel, requirements

Uuid = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
]
"""A lowercase UUID in its canonical text form. Every record id and reference id is one."""

Sha256Hex = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
"""Lowercase hexadecimal SHA-256 (64 characters). Computed only by the integrity engine."""

DecimalString = Annotated[str, StringConstraints(pattern=r"^(0|[1-9][0-9]*)$")]
"""A non-negative whole number as text, with no sign, no leading zeros and no size limit. Used
for money (paise) and quantities so large values never pass through a floating-point number."""

MAX_SAFE_INTEGER = 2**53 - 1
"""Largest integer a canonical JSON number may hold (INTEGRITY_SPEC section 4)."""


def _whole_seconds(value: dt.datetime) -> dt.datetime:
    if value.microsecond != 0:
        raise ValueError("timestamps carry whole seconds only (no fraction)")
    return value


Timestamp = Annotated[AwareDatetime, AfterValidator(_whole_seconds)]
"""A date and time with a UTC offset (kept as given, for example +05:30) and whole seconds.
The text that is hashed is `YYYY-MM-DDTHH:MM:SS+HH:MM`, never `Z` (INTEGRITY_SPEC section 2)."""


class Language(StrEnum):
    """Language of user-facing text. Kannada is P1 (after native-speaker review)."""

    EN = "en"
    HI = "hi"
    KN = "kn"


class Tone(StrEnum):
    """Tone of a suggested message. The user always sends it."""

    CASUAL = "casual"
    POLITE = "polite"
    FIRM = "firm"


class TermState(StrEnum):
    """State of a term. The four values are exactly the statuses the local model returns, so the
    model adapter is a plain mapping. The UI words are Clear (stated), Ambiguous (unclear),
    Conflict (contradicted) and Missing, each with its symbol."""

    STATED = "stated"
    UNCLEAR = "unclear"
    CONTRADICTED = "contradicted"
    MISSING = "missing"


class TermOrigin(StrEnum):
    """Which part of the system proposed the value."""

    RULES = "rules"
    AI = "ai"
    BOTH = "both"
    USER = "user"


class Confidence(StrEnum):
    """Confidence shown as words. Never used alone to confirm anything."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValueKind(StrEnum):
    """Kind of a typed term value (the `kind` field of every value model)."""

    MONEY = "money"
    QUANTITY = "quantity"
    DATE = "date"
    PARTIAL_DATE = "partial_date"
    EVENT = "event"
    DURATION = "duration"
    TEXT = "text"


class DurationUnit(StrEnum):
    """Calendar unit of a duration such as 30 days."""

    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


class MoneyValue(FrozenContractModel):
    """An amount of money in integer paise, as text. The local model returns whole rupees as an
    integer; the adapter multiplies by 100 and writes the result as text.

    Requirements: FR-EXT-001, FR-EXT-003.
    """

    model_config = requirements("FR-EXT-001", "FR-EXT-003")

    kind: Literal["money"] = Field(description="Discriminator: money.")
    paise: DecimalString = Field(description="Whole paise as text, for example 4800000.")


class QuantityValue(FrozenContractModel):
    """A quantity: a whole number as text and an optional unit word.

    Requirements: FR-EXT-001, FR-EXT-003.
    """

    model_config = requirements("FR-EXT-001", "FR-EXT-003")

    kind: Literal["quantity"] = Field(description="Discriminator: quantity.")
    amount: DecimalString = Field(description="Whole number as text, for example 200.")
    unit: str | None = Field(description="Unit word from the chat, such as shirts, or null.")


class DateValue(FrozenContractModel):
    """A full calendar date with a year. Only a full date can be part of an agreed version.

    Requirements: FR-EXT-001, FR-EXT-006.
    """

    model_config = requirements("FR-EXT-001", "FR-EXT-006")

    kind: Literal["date"] = Field(description="Discriminator: date.")
    date: Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}$")] = Field(
        description="ISO 8601 date, YYYY-MM-DD."
    )

    @model_validator(mode="after")
    def real_calendar_date(self) -> "DateValue":
        try:
            dt.date.fromisoformat(self.date)
        except ValueError as error:
            raise ValueError("not a real calendar date") from error
        return self


class PartialDateValue(FrozenContractModel):
    """A date without a year, as the local model returns it (month and day). The user supplies the
    year before it can be confirmed as a DateValue.

    Requirements: FR-EXT-001, FR-EXT-006.
    """

    model_config = requirements("FR-EXT-001", "FR-EXT-006")

    kind: Literal["partial_date"] = Field(description="Discriminator: partial_date.")
    month_day: Annotated[str, StringConstraints(pattern=r"^--\d{2}-\d{2}$")] = Field(
        description="ISO 8601 truncated date without a year, --MM-DD."
    )

    @model_validator(mode="after")
    def real_month_and_day(self) -> "PartialDateValue":
        month, day = int(self.month_day[2:4]), int(self.month_day[5:7])
        try:
            dt.date(2000, month, day)  # 2000 is a leap year, so --02-29 is accepted
        except ValueError as error:
            raise ValueError("not a real month and day") from error
        return self


class EventValue(FrozenContractModel):
    """A date given as an event, for example on_delivery or on_completion.

    Requirements: FR-EXT-001.
    """

    model_config = requirements("FR-EXT-001")

    kind: Literal["event"] = Field(description="Discriminator: event.")
    event: Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]*$")] = Field(
        description="Event name defined by the playbook."
    )


class DurationValue(FrozenContractModel):
    """A length of time in calendar units, such as 30 days after delivery.

    Requirements: FR-EXT-001.
    """

    model_config = requirements("FR-EXT-001")

    kind: Literal["duration"] = Field(description="Discriminator: duration.")
    amount: int = Field(ge=0, le=MAX_SAFE_INTEGER, description="How many units.")
    unit: DurationUnit = Field(description="days, weeks or months.")


class TextValue(FrozenContractModel):
    """A text value: a name, an item, or a phrase from the playbook's value list.

    Requirements: FR-EXT-001.
    """

    model_config = requirements("FR-EXT-001")

    kind: Literal["text"] = Field(description="Discriminator: text.")
    text: str = Field(description="The text.")


TermValue = Annotated[
    MoneyValue
    | QuantityValue
    | DateValue
    | PartialDateValue
    | EventValue
    | DurationValue
    | TextValue,
    Field(discriminator="kind"),
]
"""A typed term value. Contradiction checks and canonical hashing work on these, not on text.
Requirements: FR-EXT-001, FR-FLG-003."""


class MessageSourceRef(FrozenContractModel):
    """Points at a chat message. Requirements: FR-EXT-002."""

    model_config = requirements("FR-EXT-002")

    kind: Literal["message"] = Field(description="Discriminator: this reference is a message.")
    message_id: Uuid = Field(description="Id of the Message the value came from.")
    quote: str | None = Field(
        default=None, description="Exact text copied from the message, used for grounding."
    )


class VoiceSourceRef(FrozenContractModel):
    """Points at a time range of a voice note, for play the moment. Times are integer
    milliseconds from the start of the audio.

    Requirements: FR-EXT-002, FR-PLM-001.
    """

    model_config = requirements("FR-EXT-002", "FR-PLM-001")

    kind: Literal["voice"] = Field(description="Discriminator: this reference is a voice clip.")
    voice_note_id: Uuid = Field(description="Id of the VoiceNote the value came from.")
    start_ms: int = Field(ge=0, le=MAX_SAFE_INTEGER, description="Start of the clip in ms.")
    end_ms: int = Field(ge=0, le=MAX_SAFE_INTEGER, description="End of the clip in ms.")
    quote: str | None = Field(
        default=None, description="Exact transcript text for the clip, used for grounding."
    )

    @model_validator(mode="after")
    def end_not_before_start(self) -> "VoiceSourceRef":
        if self.end_ms < self.start_ms:
            raise ValueError("end_ms must not be before start_ms")
        return self


SourceRef = Annotated[MessageSourceRef | VoiceSourceRef, Field(discriminator="kind")]
"""Where a term, flag or recap line came from: a message id, or a voice note plus start and
end milliseconds. Requirements: FR-EXT-002, FR-PLM-001."""


class PlaybookRef(FrozenContractModel):
    """Names the playbook and version a deal uses. The playbook itself (required terms, weights,
    rules, hints, templates) stays in playbooks/*.yaml and is never copied into contracts.

    Requirements: FR-PBK-001, FR-PBK-002.
    """

    model_config = requirements("FR-PBK-001", "FR-PBK-002")

    key: str = Field(description="Playbook key, for example the file name without extension.")
    version: int = Field(ge=1, description="Playbook version the analysis was run with.")
