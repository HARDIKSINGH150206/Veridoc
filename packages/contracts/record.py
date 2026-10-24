"""Record contracts: versions, diff, receipt, verification and dispute pack (Area 3)."""

from enum import StrEnum
from typing import Literal

from pydantic import Field

from .analysis import Term
from .base import FrozenContractModel, requirements
from .common import PlaybookRef, Sha256Hex, Timestamp


class DiffChange(StrEnum):
    """Change of a term between two versions."""

    NO_CHANGE = "no_change"
    CHANGED = "changed"
    ADDED = "added"
    REMOVED = "removed"


class Verdict(StrEnum):
    """Result of verifying a receipt bundle."""

    UNCHANGED = "unchanged"
    ALTERED = "altered"


class CheckName(StrEnum):
    """The separate checks shown on the verify page."""

    CHAIN = "chain"
    MERKLE_ROOT = "merkle_root"
    TIMESTAMP_ORDER = "timestamp_order"
    ANCHOR = "anchor"


class CheckStatus(StrEnum):
    """Outcome of one check. Shown as a symbol and a word."""

    PASS = "pass"
    FAIL = "fail"
    NOT_ANCHORED = "not_anchored"


class PackPartName(StrEnum):
    """Parts of a dispute pack."""

    TIMELINE = "timeline"
    EVIDENCE_INDEX = "evidence_index"
    TERMS_ALL_VERSIONS = "terms_all_versions"
    CERTIFICATE_DRAFT = "certificate_draft"
    VERIFICATION_GUIDE = "verification_guide"
    RECEIPT_BUNDLE = "receipt_bundle"


class AgreementVersion(FrozenContractModel):
    """A numbered version of the agreed terms, chained to the previous one by hash. Never edited,
    only superseded.

    Requirements: FR-VER-001, FR-VER-003, FR-VLT-003, FR-VLT-007.
    """

    model_config = requirements("FR-VER-001", "FR-VER-003", "FR-VLT-003", "FR-VLT-007")

    id: str = Field(description="Stable id of the version.")
    deal_id: str = Field(description="Deal this version belongs to.")
    n: int = Field(ge=1, description="Version number, starting at 1.")
    playbook: PlaybookRef = Field(description="Playbook and version used.")
    terms: tuple[Term, ...] = Field(description="Confirmed terms (all have confirmed_at set).")
    terms_digest: Sha256Hex = Field(description="Hash of the canonical terms set.")
    root: Sha256Hex = Field(description="Merkle root at the moment of recording.")
    link: Sha256Hex = Field(description="Version-chain link hash.")
    prev_link: Sha256Hex | None = Field(description="Previous link hash, or null for version 1.")
    reason_message_id: str | None = Field(
        description="Message that caused this change, or null for version 1."
    )
    created_at: Timestamp = Field(description="Device-clock time of recording.")


class TermDiffRow(FrozenContractModel):
    """One row of the version diff table.

    Requirements: FR-VER-002.
    """

    model_config = requirements("FR-VER-002")

    term_key: str = Field(description="Term key.")
    before: str | None = Field(description="Value in the earlier version, or null.")
    after: str | None = Field(description="Value in the later version, or null.")
    change: DiffChange = Field(description="no_change, changed, added or removed.")


class VersionDiff(FrozenContractModel):
    """Difference between two versions. Unchanged rows stay in the list for context.

    Requirements: FR-VER-002, FR-VER-003.
    """

    model_config = requirements("FR-VER-002", "FR-VER-003")

    deal_id: str = Field(description="Deal the versions belong to.")
    from_n: int = Field(ge=1, description="Earlier version number.")
    to_n: int = Field(ge=1, description="Later version number.")
    rows: tuple[TermDiffRow, ...] = Field(description="One row per term in either version.")
    reason_message_id: str | None = Field(description="Message that explains the change.")


class ChainLink(FrozenContractModel):
    """One entry of the version chain inside a receipt.

    Requirements: FR-VLT-003, FR-VFY-002.
    """

    model_config = requirements("FR-VLT-003", "FR-VFY-002")

    version_n: int = Field(ge=1, description="Version number.")
    terms_digest: Sha256Hex = Field(description="Hash of the canonical terms set.")
    root: Sha256Hex = Field(description="Merkle root at that version.")
    link: Sha256Hex = Field(description="Link hash.")


class Anchor(FrozenContractModel):
    """Independent timestamp record (P1). Only a hash is ever anchored.

    Requirements: FR-ANC-001.
    """

    model_config = requirements("FR-ANC-001")

    network: str = Field(description="Network name, from configuration.")
    tx: str = Field(description="Transaction reference.")
    block_time: Timestamp = Field(description="Block time reported by the network.")


class Receipt(FrozenContractModel):
    """The tamper-evident record: commitment, chain and time. The time is the device clock unless
    anchored. It shows the record was not changed after saving; it does not prove the original
    chat export was genuine.

    Requirements: FR-VLT-001, FR-VLT-002, FR-VLT-003, FR-VFY-001.
    """

    model_config = requirements("FR-VLT-001", "FR-VLT-002", "FR-VLT-003", "FR-VFY-001")

    spec_version: str = Field(description="Version of docs/INTEGRITY_SPEC.md that was followed.")
    deal_id: str = Field(description="Deal the receipt covers.")
    leaf_count: int = Field(ge=1, description="Number of evidence leaves covered.")
    root: Sha256Hex = Field(description="Current Merkle root.")
    chain: tuple[ChainLink, ...] = Field(description="Version chain in order.")
    recorded_at: Timestamp = Field(description="Device-clock time of recording.")
    anchor: Anchor | None = Field(description="Anchor record, or null if not anchored.")
    receipt_hash: Sha256Hex = Field(description="Hash of the canonical receipt.")


class VerifyCheck(FrozenContractModel):
    """One line of the verify result.

    Requirements: FR-VFY-002.
    """

    model_config = requirements("FR-VFY-002")

    name: CheckName = Field(description="Which check.")
    status: CheckStatus = Field(description="pass, fail or not_anchored.")
    detail: str | None = Field(description="Plain-language detail, for example 4 of 4 links.")


class FirstDifference(FrozenContractModel):
    """The first item that does not match, named for the user.

    Requirements: FR-VFY-004.
    """

    model_config = requirements("FR-VFY-004")

    kind: Literal["message", "voice_audio", "transcript", "chain_link", "other_leaf"] = Field(
        description="What kind of item differs."
    )
    ref: str = Field(description="Message number, voice-note id, transcript id or version number.")


class VerifyResult(FrozenContractModel):
    """Outcome of verifying a bundle: unchanged, or altered with the first differing item.

    Requirements: FR-VFY-002, FR-VFY-003, FR-VFY-004, FR-VFY-005.
    """

    model_config = requirements("FR-VFY-002", "FR-VFY-003", "FR-VFY-004", "FR-VFY-005")

    verdict: Verdict = Field(description="unchanged or altered.")
    spec_version: str = Field(description="Specification version the verifier followed.")
    checks: tuple[VerifyCheck, ...] = Field(description="Each check with its own result.")
    first_difference: FirstDifference | None = Field(
        description="Set when the verdict is altered, else null."
    )


class PackPart(FrozenContractModel):
    """One switchable part of a dispute pack.

    Requirements: FR-DSP-001.
    """

    model_config = requirements("FR-DSP-001")

    name: PackPartName = Field(description="Which part.")
    included: bool = Field(description="Whether the user left it switched on.")


class DisputePackManifest(FrozenContractModel):
    """What a dispute pack (a court-ready evidence package) contains. Not legal advice. The
    certificate is always an unsigned draft.

    Requirements: FR-DSP-001, FR-DSP-002, FR-DSP-003, FR-DSP-004.
    """

    model_config = requirements("FR-DSP-001", "FR-DSP-002", "FR-DSP-003", "FR-DSP-004")

    deal_id: str = Field(description="Deal the pack was built from.")
    parts: tuple[PackPart, ...] = Field(description="Parts and whether each is included.")
    certificate_status: Literal["unsigned_draft"] = Field(
        description="The Section 63 BSA certificate is always an unsigned draft."
    )
    disclaimer_shown: bool = Field(description="True once the disclaimer was shown before export.")
    masked: bool = Field(description="True if the P1 privacy mask was applied.")
    page_count: int | None = Field(ge=0, description="Estimated or final page count.")
    size_bytes: int | None = Field(ge=0, description="Estimated or final size in bytes.")
    file_digest: Sha256Hex | None = Field(description="Hash of the exported file, or null.")
    created_at: Timestamp = Field(description="When the manifest was made.")
