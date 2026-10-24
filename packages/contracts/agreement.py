"""Agreement contracts: Blind Handshake, recap, echo code and confirmation (Area 1)."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from .base import FrozenContractModel, requirements
from .common import Language, Sha256Hex, SourceRef, Timestamp, ValueType

CrockfordCode = Annotated[str, StringConstraints(pattern=r"^[0-9ABCDEFGHJKMNPQRSTVWXYZ]{4}$")]
"""Four characters from the Crockford base32 alphabet (no I, L, O or U)."""


class HandshakeMode(StrEnum):
    """How the counterparty answered. Reply mode is primary; handover mode is the demo mode."""

    REPLY = "reply"
    HANDOVER = "handover"


class ConfirmationState(StrEnum):
    """Confirmation states for a party."""

    SENT = "sent"
    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"


class ConfirmationFailure(StrEnum):
    """Why a pasted reply did not confirm."""

    NO_CODE_FOUND = "no_code_found"
    CODE_MISMATCH = "code_mismatch"
    STALE_CODE = "stale_code"
    WRONG_SENDER = "wrong_sender"
    DECLINED = "declined"


class HandshakeQuestion(FrozenContractModel):
    """A key question both sides answer privately. Questions come from the playbook.

    Requirements: FR-HSK-001.
    """

    model_config = requirements("FR-HSK-001")

    term_key: str = Field(description="Playbook term key the question is about.")
    prompt: str = Field(description="Question text from the playbook template.")
    language: Language = Field(description="Language of the prompt.")
    value_type: ValueType = Field(description="Type of answer expected.")


class HandshakeAnswer(FrozenContractModel):
    """One answer to one question.

    Requirements: FR-HSK-001, FR-HSK-004.
    """

    model_config = requirements("FR-HSK-001", "FR-HSK-004")

    term_key: str = Field(description="Question this answers.")
    value: str = Field(description="Answer in the same format as Term.value.")
    raw: str | None = Field(description="Answer as the person wrote it.")


class SealedAnswers(FrozenContractModel):
    """A party's whole answer set, hashed and timestamped. The answers stay hidden (null) until
    both sets are sealed. The first party must be sealed before the second can submit.

    Requirements: FR-HSK-002, FR-HSK-003, FR-HSK-004, FR-HSK-007.
    """

    model_config = requirements("FR-HSK-002", "FR-HSK-003", "FR-HSK-004", "FR-HSK-007")

    deal_id: str = Field(description="Deal this handshake belongs to.")
    party_id: str = Field(description="Participant who answered.")
    order: Literal[1, 2] = Field(description="1 for the party sealed first, 2 for the second.")
    mode: HandshakeMode = Field(description="reply or handover.")
    seal_hash: Sha256Hex = Field(description="Hash of the salted, canonical answer set.")
    sealed_at: Timestamp = Field(description="Device-clock time of sealing.")
    revealed_at: Timestamp | None = Field(description="When both sets were revealed, or null.")
    answers: tuple[HandshakeAnswer, ...] | None = Field(
        description="The answers. Null until revealed; never returned before both are sealed."
    )


class RecapLine(FrozenContractModel):
    """One line of the recap with the evidence it came from.

    Requirements: FR-RCP-001, FR-RCP-004.
    """

    model_config = requirements("FR-RCP-001", "FR-RCP-004")

    term_key: str = Field(description="Confirmed term this line states.")
    text: str = Field(description="Line text from the playbook template.")
    sources: tuple[SourceRef, ...] = Field(description="Messages or clips the line links to.")


class EchoCode(FrozenContractModel):
    """The four-character code the counterparty replies with. It binds a reply to one exact
    recap; it is not authentication. Derivation is in docs/INTEGRITY_SPEC.md section 7.

    Requirements: FR-ECH-001, FR-ECH-002, FR-ECH-004.
    """

    model_config = requirements("FR-ECH-001", "FR-ECH-002", "FR-ECH-004")

    code: CrockfordCode = Field(description="The code, upper case, for example as sent in chat.")
    recap_hash: Sha256Hex = Field(description="Hash of the recap the code was derived from.")
    version_n: int = Field(ge=1, description="Agreement version the recap belongs to.")


class Recap(FrozenContractModel):
    """A short plain-language summary built only from confirmed terms using fixed templates.

    Requirements: FR-RCP-001, FR-RCP-002, FR-RCP-003, FR-RCP-004.
    """

    model_config = requirements("FR-RCP-001", "FR-RCP-002", "FR-RCP-003", "FR-RCP-004")

    id: str = Field(description="Stable id of the recap.")
    deal_id: str = Field(description="Deal this recap belongs to.")
    version_n: int = Field(ge=1, description="Agreement version it summarises.")
    language: Language = Field(description="Language of the text.")
    lines: tuple[RecapLine, ...] = Field(description="Lines in order.")
    text: str = Field(description="The exact text copied to WhatsApp, including the code line.")
    recap_hash: Sha256Hex = Field(description="Hash of the canonical recap object.")
    echo_code: EchoCode = Field(description="Code derived from recap_hash.")
    created_at: Timestamp = Field(description="When the recap was built.")


class Confirmation(FrozenContractModel):
    """A party's confirmation state for a recap. The pasted reply is stored as evidence.

    Requirements: FR-ECH-002, FR-ECH-003, FR-ECH-004.
    """

    model_config = requirements("FR-ECH-002", "FR-ECH-003", "FR-ECH-004")

    id: str = Field(description="Stable id of the confirmation record.")
    recap_id: str = Field(description="Recap being confirmed.")
    party_id: str = Field(description="Participant who confirms.")
    state: ConfirmationState = Field(description="sent, confirmed or not_confirmed.")
    reply_text: str | None = Field(description="The pasted WhatsApp reply, or null.")
    reply_ts: Timestamp | None = Field(description="Time of the reply in the chat, or null.")
    sender_entered_by_user: bool = Field(
        description="True when the user chose the sender because the paste had none."
    )
    failure: ConfirmationFailure | None = Field(description="Why it failed, or null.")
    checked_at: Timestamp | None = Field(description="When the reply was checked, or null.")
