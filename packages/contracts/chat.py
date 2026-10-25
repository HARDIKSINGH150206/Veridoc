"""Chat input contracts: people, messages, voice notes and transcripts (Area 1 produces them)."""

from enum import StrEnum

from pydantic import Field, model_validator

from .base import FrozenContractModel, requirements
from .common import MAX_SAFE_INTEGER, Language, Sha256Hex, Timestamp, Uuid


class ParticipantRole(StrEnum):
    """Whether a chat participant is one of the two deal parties or only context."""

    PARTY = "party"
    CONTEXT = "context"


class MessageOrigin(StrEnum):
    """How a message entered VeriDoc."""

    EXPORT = "export"
    PASTE = "paste"
    SIMULATOR = "simulator"


class TranscriptionStatus(StrEnum):
    """State of a voice note's transcription."""

    TRANSCRIBED = "transcribed"
    NOT_TRANSCRIBED = "not_transcribed"
    FAILED = "failed"


class Participant(FrozenContractModel):
    """A person in the chat. The user picks which one is themselves.

    Requirements: FR-IMP-004, FR-IMP-005.
    """

    model_config = requirements("FR-IMP-004", "FR-IMP-005")

    id: Uuid = Field(description="Stable id of the participant inside the deal.")
    display_name: str = Field(description="Name as it appears in the chat export.")
    role: ParticipantRole = Field(description="party for the two deal parties, else context.")
    is_me: bool = Field(description="True for the primary user (the person running VeriDoc).")


class Message(FrozenContractModel):
    """One chat message in the order of the export. Immutable after import. Every field is part
    of the hashed record (INTEGRITY_SPEC section 4).

    Requirements: FR-IMP-001, FR-IMP-002, FR-IMP-006, FR-IMP-008.
    """

    model_config = requirements("FR-IMP-001", "FR-IMP-002", "FR-IMP-006", "FR-IMP-008")

    id: Uuid = Field(description="Stable id of the message.")
    deal_id: Uuid = Field(description="Deal this message belongs to.")
    seq: int = Field(ge=1, description="Position in the chat, starting at 1. Used as #<seq>.")
    sender_id: Uuid = Field(description="Id of the Participant who sent it.")
    ts: Timestamp = Field(description="Time the message was sent, whole seconds with an offset.")
    text: str = Field(description="Message text. Treated as data, never as instructions.")
    attachment_hash: Sha256Hex | None = Field(
        description="Hash (file name) of the attached file in the evidence folder, if any."
    )
    is_system: bool = Field(description="True for system lines such as encryption notices.")
    origin: MessageOrigin = Field(description="export, paste or simulator.")


class TranscriptSpan(FrozenContractModel):
    """One timed piece of a transcript. Times are integer milliseconds. The confidence is shown
    to the user and is not part of the hashed span record.

    Requirements: FR-VOI-001, FR-VOI-003, FR-PLM-001.
    """

    model_config = requirements("FR-VOI-001", "FR-VOI-003", "FR-PLM-001")

    start_ms: int = Field(
        ge=0, le=MAX_SAFE_INTEGER, description="Start in ms from the audio start."
    )
    end_ms: int = Field(ge=0, le=MAX_SAFE_INTEGER, description="End in ms from the audio start.")
    text: str = Field(description="Transcribed text for this span.")
    confidence: float = Field(
        ge=0, le=1, description="Speech model confidence from 0 to 1, shown to the user as words."
    )

    @model_validator(mode="after")
    def end_not_before_start(self) -> "TranscriptSpan":
        if self.end_ms < self.start_ms:
            raise ValueError("end_ms must not be before start_ms")
        return self


class Transcript(FrozenContractModel):
    """The text of a voice note. A user correction creates a new Transcript, never an edit. Each
    span is hashed as its own leaf (INTEGRITY_SPEC, prefix 0x12).

    Requirements: FR-VOI-001, FR-VOI-002, FR-VOI-003.
    """

    model_config = requirements("FR-VOI-001", "FR-VOI-002", "FR-VOI-003")

    id: Uuid = Field(description="Stable id of this transcript.")
    voice_note_id: Uuid = Field(description="VoiceNote this transcript belongs to.")
    model: str = Field(description="Name of the speech model that produced it.")
    model_version: str = Field(description="Version or hash label of that speech model.")
    language: Language = Field(description="Detected language of the audio.")
    spans: tuple[TranscriptSpan, ...] = Field(description="Timed spans in order.")
    supersedes_id: Uuid | None = Field(
        description="Id of the Transcript this one corrects, or null for the first."
    )
    created_at: Timestamp = Field(description="When this transcript was created.")


class VoiceNote(FrozenContractModel):
    """A voice note from the chat. The audio and its transcript are hashed separately, so the
    transcript is referenced by id and not embedded.

    Requirements: FR-IMP-002, FR-VOI-001, FR-VOI-002.
    """

    model_config = requirements("FR-IMP-002", "FR-VOI-001", "FR-VOI-002")

    id: Uuid = Field(description="Stable id of the voice note.")
    deal_id: Uuid = Field(description="Deal this voice note belongs to.")
    seq: int = Field(ge=1, description="Position among the deal's evidence items.")
    message_id: Uuid | None = Field(description="Message that carried the audio, if known.")
    sender_id: Uuid = Field(description="Id of the Participant who sent it.")
    ts: Timestamp = Field(description="Time the voice note was sent, whole seconds with an offset.")
    audio_hash: Sha256Hex = Field(description="Hash (and file name) of the audio in the vault.")
    duration_ms: int = Field(ge=0, le=MAX_SAFE_INTEGER, description="Length of the audio in ms.")
    status: TranscriptionStatus = Field(description="Whether a transcript exists.")
    transcript_id: Uuid | None = Field(description="Id of the current Transcript, or null.")
