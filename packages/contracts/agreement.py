"""Agreement contracts: Blind Handshake, recap, echo code and confirmation (Area 1)."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from .base import FrozenContractModel, requirements
from .common import (
    Language,
    Sha256Hex,
    SourceRef,
    TermValue,
    Timestamp,
    Uuid,
    ValueKind,
)

CrockfordCode = Annotated[str, StringConstraints(pattern=r"^[0-9ABCDEFGHJKMNPQRSTVWXYZ]{4}$")]
"""Four characters from the Crockford base32 alphabet (no I, L, O or U)."""


class HandshakeMode(StrEnum):
    """How the counterparty answered. Reply mode is primary; handover mode is the demo mode."""

    REPLY = "reply"
    HANDOVER = "handover"


class RevealResult(StrEnum):
    """Result of comparing the two parties' answers to one question."""

    MATCH = "match"
    MISMATCH = "mismatch"


class ConfirmationState(StrEnum):
    """Confirmation states for a party."""

    SENT = "sent"
    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"


class ConfirmationFailure(StrEnum):
    """Why a pasted reply did not confirm. The starting set decided on 2026-10-25."""

    CODE_MISMATCH = "code_mismatch"
    WRONG_SENDER = "wrong_sender"
    RECAP_CHANGED = "recap_changed"
    MALFORMED_REPLY = "malformed_reply"
    DECLINED = "declined"


class HandshakeQuestion(FrozenContractModel):
    """A key question both sides answer privately. Questions come from the playbook.

    Requirements: FR-HSK-001.
    """

    model_config = requirements("FR-HSK-001")

    term_key: str = Field(description="Playbook term key the question is about.")
    prompt: str = Field(description="Question text from the playbook template.")
    language: Language = Field(description="Language of the prompt.")
    value_kind: ValueKind = Field(description="Kind of answer expected.")


class HandshakeAnswer(FrozenContractModel):
    """One answer to one question.

    Requirements: FR-HSK-001, FR-HSK-004.
    """

    model_config = requirements("FR-HSK-001", "FR-HSK-004")

    term_key: str = Field(description="Question this answers.")
    value: TermValue = Field(description="Typed answer, in the same format as Term.value.")
    raw: str | None = Field(description="Answer as the person wrote it.")


class SealedAnswers(FrozenContractModel):
    """A party's whole answer set, hashed and timestamped. The answers stay hidden (null) until
    both sets are sealed. The first party must be sealed before the second can submit.

    Requirements: FR-HSK-002, FR-HSK-003, FR-HSK-004, FR-HSK-007.
    """

    model_config = requirements("FR-HSK-002", "FR-HSK-003", "FR-HSK-004", "FR-HSK-007")

    deal_id: Uuid = Field(description="Deal this handshake belongs to.")
    party_id: Uuid = Field(description="Participant who answered.")
    order: Literal[1, 2] = Field(description="1 for the party sealed first, 2 for the second.")
    mode: HandshakeMode = Field(description="reply or handover.")
    seal_hash: Sha256Hex = Field(description="Hash of the salted, canonical answer set.")
    sealed_at: Timestamp = Field(description="Device-clock time of sealing.")
    revealed_at: Timestamp | None = Field(description="When both sets were revealed, or null.")
    answers: tuple[HandshakeAnswer, ...] | None = Field(
        description="The answers. Null until revealed; never returned before both are sealed."
    )


class HandshakeRevealRow(FrozenContractModel):
    """One row of the side-by-side reveal: both answers and whether they match.

    Requirements: FR-HSK-004.
    """

    model_config = requirements("FR-HSK-004")

    term_key: str = Field(description="Question the row is about.")
    first: HandshakeAnswer = Field(description="Answer of the party sealed first.")
    second: HandshakeAnswer = Field(description="Answer of the party sealed second.")
    result: RevealResult = Field(description="match or mismatch.")
    difference_code: str | None = Field(
        description="Code of the difference template (for example days_apart); null on a match."
    )
    difference_params: dict[str, str] = Field(
        description="Values the template inserts, as text (for example the number of days)."
    )


class HandshakeReveal(FrozenContractModel):
    """The side-by-side result shown after both answer sets are sealed (screen S5).

    Requirements: FR-HSK-004, FR-HSK-005.
    """

    model_config = requirements("FR-HSK-004", "FR-HSK-005")

    deal_id: Uuid = Field(description="Deal this handshake belongs to.")
    revealed_at: Timestamp = Field(description="When the answers were revealed.")
    rows: tuple[HandshakeRevealRow, ...] = Field(description="One row per question.")


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
    recap; it is not authentication. It is derived from the hash of the recap WITHOUT the code
    line and attached afterwards (docs/INTEGRITY_SPEC.md section 7).

    Requirements: FR-ECH-001, FR-ECH-002, FR-ECH-004.
    """

    model_config = requirements("FR-ECH-001", "FR-ECH-002", "FR-ECH-004")

    code: CrockfordCode = Field(description="The code, upper case.")
    recap_hash: Sha256Hex = Field(description="Hash of the recap content without the code.")
    version_n: int = Field(ge=1, description="Agreement version the recap belongs to.")


class Recap(FrozenContractModel):
    """A short plain-language summary built only from confirmed terms using fixed templates.

    Order of work: body_text is built, then recap_hash is computed over {deal_id, version_n,
    language, lines, body_text}, then the echo code is derived from that hash, then `text` is
    body_text plus the code line. `text` and echo_code are NOT part of the hashed content.

    Requirements: FR-RCP-001, FR-RCP-002, FR-RCP-003, FR-RCP-004, FR-ECH-001.
    """

    model_config = requirements(
        "FR-RCP-001", "FR-RCP-002", "FR-RCP-003", "FR-RCP-004", "FR-ECH-001"
    )

    id: Uuid = Field(description="Stable id of the recap.")
    deal_id: Uuid = Field(description="Deal this recap belongs to.")
    version_n: int = Field(ge=1, description="Agreement version it summarises.")
    language: Language = Field(description="Language of the text.")
    lines: tuple[RecapLine, ...] = Field(description="Lines in order.")
    body_text: str = Field(description="The recap text without the code line (this is hashed).")
    text: str = Field(
        description="The exact text copied to WhatsApp: body_text plus the code line."
    )
    recap_hash: Sha256Hex = Field(description="Hash of the canonical recap content (no code).")
    echo_code: EchoCode = Field(description="Code derived from recap_hash.")
    created_at: Timestamp = Field(description="When the recap was built.")

    @model_validator(mode="after")
    def consistent(self) -> "Recap":
        if self.echo_code.recap_hash != self.recap_hash:
            raise ValueError("echo_code.recap_hash must equal recap_hash")
        if self.echo_code.version_n != self.version_n:
            raise ValueError("echo_code.version_n must equal version_n")
        if not self.text.startswith(self.body_text):
            raise ValueError("text must start with body_text")
        if self.echo_code.code not in self.text[len(self.body_text) :]:
            raise ValueError("text must end with a line that contains the echo code")
        return self


class Confirmation(FrozenContractModel):
    """A party's confirmation state for a recap. The pasted reply is stored as evidence. Hashed
    fields (leaf 0x22): deal_id, version_n, party_id, reply_text, reply_ts, code,
    sender_entered_by_user. The state, failure and checked_at are never hashed.

    Requirements: FR-ECH-002, FR-ECH-003, FR-ECH-004.
    """

    model_config = requirements("FR-ECH-002", "FR-ECH-003", "FR-ECH-004")

    id: Uuid = Field(description="Stable id of the confirmation record.")
    recap_id: Uuid = Field(description="Recap being confirmed.")
    deal_id: Uuid = Field(description="Deal the recap belongs to.")
    version_n: int = Field(ge=1, description="Agreement version the recap belongs to.")
    party_id: Uuid = Field(description="Participant who confirms.")
    state: ConfirmationState = Field(description="sent, confirmed or not_confirmed.")
    reply_text: str | None = Field(description="The pasted WhatsApp reply, or null.")
    reply_ts: Timestamp | None = Field(description="Time of the reply in the chat, or null.")
    code: CrockfordCode | None = Field(description="The code found in the reply, or null.")
    sender_entered_by_user: bool = Field(
        description="True when the user chose the sender because the paste had none."
    )
    failure: ConfirmationFailure | None = Field(description="Why it failed, or null.")
    checked_at: Timestamp | None = Field(description="When the reply was checked, or null.")
