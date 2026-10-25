"""Analysis contracts: terms, flags, score and suggestion (Area 2 produces them)."""

from enum import StrEnum

from pydantic import Field, model_validator

from .base import ContractModel, FrozenContractModel, requirements
from .common import (
    Confidence,
    Language,
    MessageSourceRef,
    SourceRef,
    TermOrigin,
    TermState,
    TermValue,
    Timestamp,
    Tone,
    Uuid,
    VoiceSourceRef,
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
    """Another value found for the same term (a contradiction, or rules versus AI disagreement).

    Requirements: FR-FLG-003, FR-AIS-004.
    """

    model_config = requirements("FR-FLG-003", "FR-AIS-004")

    value: TermValue = Field(description="The alternative value, typed like Term.value.")
    origin: TermOrigin = Field(description="Who proposed this alternative.")
    sources: tuple[SourceRef, ...] = Field(description="Where this alternative came from.")


class Term(ContractModel):
    """One agreed fact in a deal, proposed by rules or AI and confirmed by a person.

    The four states are the statuses the local model returns. Rules that always hold: a value is
    present only when the state is stated; an unclear reason only when unclear; a missing term has
    no sources; and a term can be confirmed only when it is stated with a concrete value.
    Mutable only until it becomes an AgreedTerm in a version. Nothing reaches the vault before
    confirmed_at is set.

    Requirements: FR-EXT-001, FR-EXT-002, FR-EXT-005, FR-EXT-006, FR-AIS-001, FR-AIS-004.
    """

    model_config = requirements(
        "FR-EXT-001", "FR-EXT-002", "FR-EXT-005", "FR-EXT-006", "FR-AIS-001", "FR-AIS-004"
    )

    id: Uuid = Field(description="Stable id of the term.")
    deal_id: Uuid = Field(description="Deal this term belongs to.")
    key: str = Field(description="Term key defined by the playbook, for example unit_price.")
    value: TermValue | None = Field(
        description="Typed value. Null unless the state is stated (as the model returns it)."
    )
    raw: str | None = Field(description="Original wording from the chat, for display.")
    state: TermState = Field(description="stated, unclear, contradicted or missing.")
    unclear_reason: str | None = Field(
        description="Reason code from the playbook (for example relative_date); only when unclear."
    )
    origin: TermOrigin = Field(description="rules, ai, both or user.")
    confidence: Confidence = Field(description="high, medium or low.")
    needs_review: bool = Field(description="True when rules and AI disagree or voice is unclear.")
    sources: list[SourceRef] = Field(
        description="Messages or voice clips the value came from. Empty only when missing."
    )
    alternatives: list[AlternativeValue] = Field(
        description="Other values for a contradiction or a rules versus AI disagreement."
    )
    confirmed_at: Timestamp | None = Field(
        description="When the primary user confirmed the value, or null if not yet confirmed."
    )
    confirmed_by: Uuid | None = Field(
        description="Participant who confirmed it (the primary user), or null."
    )
    acknowledged_by_other: bool = Field(
        description="True when the other party agreed in the chat or in a confirmed recap."
    )

    @model_validator(mode="after")
    def structural_rules(self) -> "Term":
        stated = self.state is TermState.STATED
        if stated != (self.value is not None):
            raise ValueError("a value is present exactly when the state is stated")
        if (self.unclear_reason is not None) and self.state is not TermState.UNCLEAR:
            raise ValueError("an unclear reason is only allowed when the state is unclear")
        if self.state is TermState.MISSING and self.sources:
            raise ValueError("a missing term has no sources")
        if self.confirmed_at is not None:
            if not stated:
                raise ValueError("only a stated term with a concrete value can be confirmed")
            if self.confirmed_by is None:
                raise ValueError("a confirmed term records who confirmed it")
        elif self.confirmed_by is not None:
            raise ValueError("confirmed_by is set only together with confirmed_at")
        return self


class Flag(ContractModel):
    """Something unclear, missing or contradictory. The reason is a code plus parameters; the
    text for the user is rendered from per-language templates, so one flag reads in any language.

    Requirements: FR-FLG-001, FR-FLG-002, FR-FLG-003, FR-FLG-004, FR-FLG-005, FR-FLG-006.
    """

    model_config = requirements(
        "FR-FLG-001", "FR-FLG-002", "FR-FLG-003", "FR-FLG-004", "FR-FLG-005", "FR-FLG-006"
    )

    id: Uuid = Field(description="Stable id of the flag.")
    deal_id: Uuid = Field(description="Deal this flag belongs to.")
    kind: FlagKind = Field(description="ambiguous, missing, contradiction or another kind.")
    rule_id: str = Field(description="Id of the playbook rule or detector that raised it.")
    term_key: str | None = Field(description="Term the flag is about, or null for the whole deal.")
    reason_code: str = Field(description="Code of the reason template, for example relative_date.")
    reason_params: dict[str, str] = Field(
        description="Values the template inserts, as text (for example message numbers)."
    )
    sources: list[SourceRef] = Field(
        description="Evidence. A contradiction between a message and a voice clip lists both."
    )
    created_at: Timestamp = Field(description="When the flag was raised.")
    resolved_at: Timestamp | None = Field(description="When it was resolved, or null.")

    @property
    def cross_modal(self) -> bool:
        """True when the evidence mixes chat text and a voice clip (text versus voice)."""
        has_text = any(isinstance(s, MessageSourceRef) for s in self.sources)
        has_voice = any(isinstance(s, VoiceSourceRef) for s in self.sources)
        return has_text and has_voice


class ScoreBreakdownItem(FrozenContractModel):
    """The score parts of one required term. Weight comes from the playbook.

    Requirements: FR-SCO-001, FR-SCO-002.
    """

    model_config = requirements("FR-SCO-001", "FR-SCO-002")

    term_key: str = Field(description="Term key from the playbook.")
    weight: int = Field(ge=0, description="Weight from the playbook (never defaulted here).")
    present: bool = Field(description="A confirmed concrete value exists.")
    clear: bool = Field(description="The term state is stated.")
    acknowledged: bool = Field(description="Both parties are on record for the value.")
    points: float = Field(ge=0, description="Points earned by the term, computed by the engine.")


class EvidenceScore(FrozenContractModel):
    """Evidence Strength from 0 to 100 with its full breakdown.

    Requirements: FR-SCO-001, FR-SCO-002, FR-SCO-003.
    """

    model_config = requirements("FR-SCO-001", "FR-SCO-002", "FR-SCO-003")

    deal_id: Uuid = Field(description="Deal the score belongs to.")
    ts: Timestamp = Field(description="When the score was computed.")
    total: int = Field(ge=0, le=100, description="Rounded score from 0 to 100.")
    breakdown: tuple[ScoreBreakdownItem, ...] = Field(description="One item per required term.")
    trigger: str = Field(description="What caused the recompute, for example import or confirm.")


class Suggestion(ContractModel):
    """One suggested next message that closes the highest-priority gap. The user sends it.

    Requirements: FR-SUG-001, FR-SUG-002, FR-SUG-003, FR-SUG-004.
    """

    model_config = requirements("FR-SUG-001", "FR-SUG-002", "FR-SUG-003", "FR-SUG-004")

    id: Uuid = Field(description="Stable id of the suggestion.")
    deal_id: Uuid = Field(description="Deal this suggestion is for.")
    target_term_keys: list[str] = Field(description="Terms the message tries to close.")
    tone: Tone = Field(description="casual, polite or firm.")
    language: Language = Field(description="Language of the text.")
    text: str = Field(description="Message text from the playbook template, filled with values.")
    created_at: Timestamp = Field(description="When it was produced.")
    copied_at: Timestamp | None = Field(
        description="When the user copied it. VeriDoc cannot know if it was sent."
    )
