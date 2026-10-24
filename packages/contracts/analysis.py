"""Analysis contracts: terms, flags, score and suggestion (Area 2 produces them)."""

from enum import StrEnum

from pydantic import Field

from .base import ContractModel, FrozenContractModel, requirements
from .common import (
    Confidence,
    Language,
    SourceRef,
    TermOrigin,
    TermState,
    Timestamp,
    Tone,
    ValueType,
)


class FlagKind(StrEnum):
    """Kind of flag. The playbook rule that raised it is in Flag.rule_id."""

    AMBIGUOUS = "ambiguous"
    MISSING = "missing"
    CONTRADICTION = "contradiction"
    UNACKNOWLEDGED = "unacknowledged"
    NEEDS_REVIEW = "needs_review"
    REGISTRATION_HINT = "registration_hint"


class AlternativeValue(FrozenContractModel):
    """Another value found for the same term (a conflict, or rules versus AI disagreement).

    Requirements: FR-FLG-003, FR-AIS-004.
    """

    model_config = requirements("FR-FLG-003", "FR-AIS-004")

    value: str = Field(description="Normalised alternative value, same format as Term.value.")
    origin: TermOrigin = Field(description="Who proposed this alternative.")
    sources: tuple[SourceRef, ...] = Field(description="Where this alternative came from.")


class Term(ContractModel):
    """One agreed fact in a deal, proposed by rules or AI and confirmed by a person.

    Mutable only until it is part of an AgreementVersion. Nothing reaches the vault before
    confirmed_at is set.

    Requirements: FR-EXT-001, FR-EXT-002, FR-EXT-005, FR-EXT-006, FR-AIS-001, FR-AIS-004.
    """

    model_config = requirements(
        "FR-EXT-001", "FR-EXT-002", "FR-EXT-005", "FR-EXT-006", "FR-AIS-001", "FR-AIS-004"
    )

    id: str = Field(description="Stable id of the term inside the deal.")
    deal_id: str = Field(description="Deal this term belongs to.")
    key: str = Field(description="Term key defined by the playbook, for example a price key.")
    value_type: ValueType = Field(description="Type of the value, copied from the playbook.")
    value: str | None = Field(
        description=(
            "Normalised value as a string. Money is integer paise, dates are ISO 8601, "
            "quantities are plain integers. Null when the term is missing."
        )
    )
    unit: str | None = Field(description="Unit of the value, for example paise or a goods unit.")
    raw: str | None = Field(description="Original wording from the chat, for display.")
    state: TermState = Field(description="clear, ambiguous, missing or conflict.")
    origin: TermOrigin = Field(description="rules, ai, both or user.")
    confidence: Confidence = Field(description="high, medium or low.")
    needs_review: bool = Field(description="True when rules and AI disagree or voice is unclear.")
    sources: tuple[SourceRef, ...] = Field(
        description="Messages or voice clips the value came from. Empty only when missing."
    )
    alternatives: tuple[AlternativeValue, ...] = Field(
        description="Other values for a conflict or a rules versus AI disagreement."
    )
    confirmed_at: Timestamp | None = Field(
        description="When the primary user confirmed the value, or null if not yet confirmed."
    )
    acknowledged_by_other: bool = Field(
        description="True when the other party agreed in the chat or in a confirmed recap."
    )


class Flag(ContractModel):
    """Something ambiguous, missing or contradictory, with a plain-language reason.

    Requirements: FR-FLG-001, FR-FLG-002, FR-FLG-003, FR-FLG-004, FR-FLG-005, FR-FLG-006.
    """

    model_config = requirements(
        "FR-FLG-001", "FR-FLG-002", "FR-FLG-003", "FR-FLG-004", "FR-FLG-005", "FR-FLG-006"
    )

    id: str = Field(description="Stable id of the flag inside the deal.")
    deal_id: str = Field(description="Deal this flag belongs to.")
    kind: FlagKind = Field(description="ambiguous, missing, contradiction or another kind.")
    rule_id: str = Field(description="Id of the playbook rule or detector that raised it.")
    term_key: str | None = Field(description="Term the flag is about, or null for the whole deal.")
    reason: str = Field(description="Plain-language reason, one or two sentences.")
    language: Language = Field(description="Language of the reason text.")
    sources: tuple[SourceRef, ...] = Field(
        description="Evidence. A contradiction between a message and a voice clip lists both."
    )
    created_at: Timestamp = Field(description="When the flag was raised.")
    resolved_at: Timestamp | None = Field(description="When it was resolved, or null.")


class ScoreBreakdownItem(FrozenContractModel):
    """The score parts of one required term. Weight comes from the playbook.

    Requirements: FR-SCO-001, FR-SCO-002.
    """

    model_config = requirements("FR-SCO-001", "FR-SCO-002")

    term_key: str = Field(description="Term key from the playbook.")
    weight: int = Field(ge=0, description="Weight from the playbook (never defaulted here).")
    present: bool = Field(description="A confirmed value exists.")
    clear: bool = Field(description="The term state is clear.")
    acknowledged: bool = Field(description="Both parties are on record for the value.")
    points: float = Field(ge=0, description="Points earned by the term, computed by the engine.")


class EvidenceScore(FrozenContractModel):
    """Evidence Strength from 0 to 100 with its full breakdown.

    Requirements: FR-SCO-001, FR-SCO-002, FR-SCO-003.
    """

    model_config = requirements("FR-SCO-001", "FR-SCO-002", "FR-SCO-003")

    deal_id: str = Field(description="Deal the score belongs to.")
    ts: Timestamp = Field(description="When the score was computed.")
    total: int = Field(ge=0, le=100, description="Rounded score from 0 to 100.")
    breakdown: tuple[ScoreBreakdownItem, ...] = Field(description="One item per required term.")
    trigger: str = Field(description="What caused the recompute, for example import or confirm.")


class Suggestion(ContractModel):
    """One suggested next message that closes the highest-priority gap. The user sends it.

    Requirements: FR-SUG-001, FR-SUG-002, FR-SUG-003, FR-SUG-004.
    """

    model_config = requirements("FR-SUG-001", "FR-SUG-002", "FR-SUG-003", "FR-SUG-004")

    id: str = Field(description="Stable id of the suggestion.")
    deal_id: str = Field(description="Deal this suggestion is for.")
    target_term_keys: tuple[str, ...] = Field(description="Terms the message tries to close.")
    tone: Tone = Field(description="casual, polite or firm.")
    language: Language = Field(description="Language of the text.")
    text: str = Field(description="Message text from the playbook template, filled with values.")
    created_at: Timestamp = Field(description="When it was produced.")
    copied_at: Timestamp | None = Field(
        description="When the user copied it. VeriDoc cannot know if it was sent."
    )
