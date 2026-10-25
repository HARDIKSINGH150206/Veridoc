"""API contracts: the live-analysis event stream, the error body and the deal summary."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from .analysis import EvidenceScore, Flag, Suggestion, Term
from .base import FrozenContractModel, requirements
from .common import DateValue, PlaybookRef, Timestamp, Uuid


class StreamStage(StrEnum):
    """Which stage of the analysis a progress event reports."""

    PARSE = "parse"
    RULES = "rules"
    VOICE = "voice"
    AI = "ai"


class DealStatus(StrEnum):
    """Status of a deal in the deals list (screen S1)."""

    DRAFT = "draft"
    AWAITING = "awaiting"
    CONFIRMED = "confirmed"


class ErrorBody(FrozenContractModel):
    """The one error body every API route returns. The UI shows the message and the hint, never a
    stack trace, and the message holds no chat content.

    Requirements: NFR-REL-001, NFR-PRV-002.
    """

    model_config = requirements("NFR-REL-001", "NFR-PRV-002")

    code: str = Field(description="Stable error code, for example vault_locked.")
    message_en: str = Field(description="Plain-language message in English.")
    message_hi: str | None = Field(description="Plain-language message in Hindi, or null.")
    hint: str | None = Field(description="What the user can do next, or null.")


class TermEvent(FrozenContractModel):
    """A term was proposed or changed.

    Requirements: FR-EXT-001.
    """

    model_config = requirements("FR-EXT-001")

    type: Literal["term"] = Field(description="Discriminator: term.")
    term: Term = Field(description="The term.")


class FlagEvent(FrozenContractModel):
    """A flag was raised or resolved.

    Requirements: FR-FLG-001.
    """

    model_config = requirements("FR-FLG-001")

    type: Literal["flag"] = Field(description="Discriminator: flag.")
    flag: Flag = Field(description="The flag.")


class ScoreEvent(FrozenContractModel):
    """The Evidence Strength score was recomputed.

    Requirements: FR-SCO-003.
    """

    model_config = requirements("FR-SCO-003")

    type: Literal["score"] = Field(description="Discriminator: score.")
    score: EvidenceScore = Field(description="The new score.")


class SuggestionEvent(FrozenContractModel):
    """A suggested next message is ready.

    Requirements: FR-SUG-001.
    """

    model_config = requirements("FR-SUG-001")

    type: Literal["suggestion"] = Field(description="Discriminator: suggestion.")
    suggestion: Suggestion = Field(description="The suggestion.")


class ProgressEvent(FrozenContractModel):
    """Progress of a slow stage, for the progress labels (voice transcription, AI refinement).

    Requirements: FR-VOI-001, FR-EXT-004.
    """

    model_config = requirements("FR-VOI-001", "FR-EXT-004")

    type: Literal["progress"] = Field(description="Discriminator: progress.")
    stage: StreamStage = Field(description="Which stage.")
    done: int = Field(ge=0, description="Items finished.")
    total: int = Field(ge=0, description="Items in total.")


class DoneEvent(FrozenContractModel):
    """The analysis finished. The stream may stay open for later messages.

    Requirements: FR-IMP-008.
    """

    model_config = requirements("FR-IMP-008")

    type: Literal["done"] = Field(description="Discriminator: done.")


class ErrorEvent(FrozenContractModel):
    """A stage failed. Nothing is lost: the rules result stands.

    Requirements: FR-SAF-001, NFR-REL-001.
    """

    model_config = requirements("FR-SAF-001", "NFR-REL-001")

    type: Literal["error"] = Field(description="Discriminator: error.")
    error: ErrorBody = Field(description="What went wrong, in plain words.")


StreamEvent = Annotated[
    TermEvent | FlagEvent | ScoreEvent | SuggestionEvent | ProgressEvent | DoneEvent | ErrorEvent,
    Field(discriminator="type"),
]
"""One event of the live-analysis stream. Requirements: FR-IMP-008, NFR-PERF-003."""


class StreamEnvelope(FrozenContractModel):
    """The envelope of every server-sent event. event_id grows by one per event so a client can
    resume with Last-Event-ID.

    Requirements: FR-IMP-008, NFR-PERF-003.
    """

    model_config = requirements("FR-IMP-008", "NFR-PERF-003")

    event_id: int = Field(ge=1, description="Sequence number of the event, from 1.")
    deal_id: Uuid = Field(description="Deal the event belongs to.")
    sent_at: Timestamp = Field(description="When the event was sent.")
    event: StreamEvent = Field(description="The event.")


class DealSummary(FrozenContractModel):
    """One row of the deals list (screen S1).

    Requirements: FR-SCO-003, FR-VER-001.
    """

    model_config = requirements("FR-SCO-003", "FR-VER-001")

    deal_id: Uuid = Field(description="Deal id.")
    title: str = Field(description="Deal title, for example the names of the two parties.")
    playbook: PlaybookRef = Field(description="Playbook the deal uses.")
    score: int = Field(ge=0, le=100, description="Current Evidence Strength.")
    open_gap_count: int = Field(ge=0, description="Missing and unclear terms.")
    conflict_count: int = Field(ge=0, description="Contradicted terms.")
    next_date: DateValue | None = Field(description="Next agreed date, or null.")
    status: DealStatus = Field(description="draft, awaiting or confirmed.")
    updated_at: Timestamp = Field(description="When the deal last changed.")
