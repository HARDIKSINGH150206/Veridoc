"""Shared enums, constrained types and small models used by several contracts."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from .base import FrozenContractModel, requirements

Sha256Hex = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
"""Lowercase hexadecimal SHA-256 (64 characters). Computed only by the integrity engine."""

Timestamp = AwareDatetime
"""A date and time that must carry a UTC offset (device clock unless anchored)."""


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
    """State of a term. Each state is shown as a symbol and a word in the UI."""

    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"
    MISSING = "missing"
    CONFLICT = "conflict"


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


class ValueType(StrEnum):
    """Type of a term value, copied from the playbook's term definition."""

    PARTY = "party"
    TEXT = "text"
    QUANTITY = "quantity"
    MONEY = "money"
    DATE = "date"
    PERCENT = "percent"
    DURATION = "duration"
    ENUM = "enum"


class MessageSourceRef(FrozenContractModel):
    """Points at a chat message. Requirements: FR-EXT-002."""

    model_config = requirements("FR-EXT-002")

    kind: Literal["message"] = Field(description="Discriminator: this reference is a message.")
    message_id: str = Field(description="Id of the Message the value came from.")
    quote: str | None = Field(
        default=None, description="Exact text copied from the message, used for grounding."
    )


class VoiceSourceRef(FrozenContractModel):
    """Points at a time range of a voice note, for play the moment.

    Requirements: FR-EXT-002, FR-PLM-001.
    """

    model_config = requirements("FR-EXT-002", "FR-PLM-001")

    kind: Literal["voice"] = Field(description="Discriminator: this reference is a voice clip.")
    voice_note_id: str = Field(description="Id of the VoiceNote the value came from.")
    start_s: float = Field(ge=0, description="Start of the clip in seconds from the start.")
    end_s: float = Field(ge=0, description="End of the clip in seconds from the start.")
    quote: str | None = Field(
        default=None, description="Exact transcript text for the clip, used for grounding."
    )

    @model_validator(mode="after")
    def end_not_before_start(self) -> "VoiceSourceRef":
        if self.end_s < self.start_s:
            raise ValueError("end_s must not be before start_s")
        return self


SourceRef = Annotated[MessageSourceRef | VoiceSourceRef, Field(discriminator="kind")]
"""Where a term, flag or recap line came from: a message id, or a voice note plus start and
end seconds. Requirements: FR-EXT-002, FR-PLM-001."""


class PlaybookRef(FrozenContractModel):
    """Names the playbook and version a deal uses. The playbook itself (required terms, weights,
    rules, hints, templates) stays in playbooks/*.yaml and is never copied into contracts.

    Requirements: FR-PBK-001, FR-PBK-002.
    """

    model_config = requirements("FR-PBK-001", "FR-PBK-002")

    key: str = Field(description="Playbook key, for example the file name without extension.")
    version: int = Field(ge=1, description="Playbook version the analysis was run with.")
