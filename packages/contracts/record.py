"""Record contracts: versions, diff, receipt, verification, dispute pack and bundle (Area 3)."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from .base import FrozenContractModel, requirements
from .common import (
    MAX_SAFE_INTEGER,
    PartialDateValue,
    PlaybookRef,
    Sha256Hex,
    SourceRef,
    TermValue,
    Timestamp,
    Uuid,
)


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


class LeafType(StrEnum):
    """Record type of a Merkle leaf, one per salted prefix of INTEGRITY_SPEC section 3."""

    MESSAGE = "message"
    VOICE_AUDIO = "voice_audio"
    TRANSCRIPT_SPAN = "transcript_span"
    HANDSHAKE_SEAL = "handshake_seal"
    ATTACHMENT = "attachment"
    TERM = "term"
    CONFIRMATION = "confirmation"


class BundleFileRole(StrEnum):
    """What a file inside a receipt bundle is for."""

    RECEIPT = "receipt"
    LEAVES = "leaves"
    CHAIN = "chain"
    MEDIA = "media"
    README = "readme"


class AgreedTerm(FrozenContractModel):
    """A confirmed term frozen into a version, so the version cannot drift from its digest. Its
    value is a full typed value: a date has a year (a partial date is not allowed here).

    Requirements: FR-EXT-005, FR-VER-001, FR-VLT-007.
    """

    model_config = requirements("FR-EXT-005", "FR-VER-001", "FR-VLT-007")

    key: str = Field(description="Term key from the playbook.")
    value: TermValue = Field(description="The confirmed typed value.")
    sources: tuple[SourceRef, ...] = Field(description="Messages or voice clips it came from.")
    confirmed_by: Uuid = Field(description="Participant who confirmed it.")
    confirmed_at: Timestamp = Field(description="When it was confirmed.")

    @model_validator(mode="after")
    def value_is_complete(self) -> "AgreedTerm":
        if isinstance(self.value, PartialDateValue):
            raise ValueError("a date without a year cannot be part of an agreed version")
        return self


class AgreementVersion(FrozenContractModel):
    """A numbered version of the agreed terms, chained to the previous one by hash. Never edited,
    only superseded. The terms are a frozen snapshot, and terms_digest is the hash of exactly that
    snapshot.

    Requirements: FR-VER-001, FR-VER-003, FR-VLT-003, FR-VLT-007.
    """

    model_config = requirements("FR-VER-001", "FR-VER-003", "FR-VLT-003", "FR-VLT-007")

    id: Uuid = Field(description="Stable id of the version.")
    deal_id: Uuid = Field(description="Deal this version belongs to.")
    version_n: int = Field(ge=1, description="Version number, starting at 1.")
    playbook: PlaybookRef = Field(description="Playbook and version used.")
    terms: tuple[AgreedTerm, ...] = Field(description="The confirmed terms of this version.")
    terms_digest: Sha256Hex = Field(description="Hash of the canonical terms snapshot.")
    root: Sha256Hex = Field(description="Merkle root at the moment of recording.")
    link: Sha256Hex = Field(description="Version-chain link hash.")
    prev_link: Sha256Hex | None = Field(description="Previous link hash, or null for version 1.")
    reason_message_id: Uuid | None = Field(
        description="Message that caused this change, or null for version 1."
    )
    created_at: Timestamp = Field(description="Device-clock time of recording.")


class TermDiffRow(FrozenContractModel):
    """One row of the version diff table.

    Requirements: FR-VER-002.
    """

    model_config = requirements("FR-VER-002")

    term_key: str = Field(description="Term key.")
    before: TermValue | None = Field(description="Value in the earlier version, or null.")
    after: TermValue | None = Field(description="Value in the later version, or null.")
    change: DiffChange = Field(description="no_change, changed, added or removed.")


class VersionDiff(FrozenContractModel):
    """Difference between two versions. Unchanged rows stay in the list for context.

    Requirements: FR-VER-002, FR-VER-003.
    """

    model_config = requirements("FR-VER-002", "FR-VER-003")

    deal_id: Uuid = Field(description="Deal the versions belong to.")
    from_version_n: int = Field(ge=1, description="Earlier version number.")
    to_version_n: int = Field(ge=1, description="Later version number.")
    rows: tuple[TermDiffRow, ...] = Field(description="One row per term in either version.")
    reason_message_id: Uuid | None = Field(description="Message that explains the change.")


class ChainLink(FrozenContractModel):
    """One entry of the version chain inside a receipt.

    Requirements: FR-VLT-003, FR-VFY-002.
    """

    model_config = requirements("FR-VLT-003", "FR-VFY-002")

    version_n: int = Field(ge=1, description="Version number.")
    terms_digest: Sha256Hex = Field(description="Hash of the canonical terms snapshot.")
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


class ReceiptBody(FrozenContractModel):
    """The content of a receipt: commitment, chain and time. This is exactly what is hashed
    (receipt_hash = H(0x40 || canonical body)); the hash is not inside the body.

    Requirements: FR-VLT-001, FR-VLT-002, FR-VLT-003, FR-VFY-001.
    """

    model_config = requirements("FR-VLT-001", "FR-VLT-002", "FR-VLT-003", "FR-VFY-001")

    spec_version: str = Field(description="Version of docs/INTEGRITY_SPEC.md that was followed.")
    deal_id: Uuid = Field(description="Deal the receipt covers.")
    leaf_count: int = Field(ge=1, le=MAX_SAFE_INTEGER, description="Number of leaves covered.")
    root: Sha256Hex = Field(description="Current Merkle root.")
    chain: tuple[ChainLink, ...] = Field(description="Version chain in order.")
    recorded_at: Timestamp = Field(description="Device-clock time of recording.")
    anchor: Anchor | None = Field(description="Anchor record, or null if not anchored.")


class Receipt(FrozenContractModel):
    """The tamper-evident record as an envelope: the body and the hash of the body. It shows the
    record was not changed after saving; it does not prove the original chat export was genuine.

    Requirements: FR-VLT-001, FR-VLT-002, FR-VLT-003, FR-VFY-001.
    """

    model_config = requirements("FR-VLT-001", "FR-VLT-002", "FR-VLT-003", "FR-VFY-001")

    body: ReceiptBody = Field(description="The hashed content.")
    receipt_hash: Sha256Hex = Field(description="Hash of the canonical body, held outside it.")


class VerifyCheck(FrozenContractModel):
    """One line of the verify result.

    Requirements: FR-VFY-002.
    """

    model_config = requirements("FR-VFY-002")

    name: CheckName = Field(description="Which check.")
    status: CheckStatus = Field(description="pass, fail or not_anchored.")
    detail: str | None = Field(description="Plain-language detail, for example 4 of 4 links.")


class FirstDifference(FrozenContractModel):
    """The first item that does not match, named for the user. One kind per leaf type, plus the
    structural records.

    Requirements: FR-VFY-004.
    """

    model_config = requirements("FR-VFY-004")

    kind: Literal[
        "message",
        "voice_audio",
        "transcript_span",
        "handshake_seal",
        "attachment",
        "term",
        "confirmation",
        "import_record",
        "chain_link",
    ] = Field(description="What kind of item differs.")
    ref: str = Field(description="Message number, voice-note id, span index, term key or version.")


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

    deal_id: Uuid = Field(description="Deal the pack was built from.")
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


class ImportRecord(FrozenContractModel):
    """The import of a chat export. export_digest is the plain SHA-256 of the raw export file,
    unnormalised. Plain record, prefix 0x16.

    Requirements: FR-IMP-001, FR-IMP-002, FR-VLT-001.
    """

    model_config = requirements("FR-IMP-001", "FR-IMP-002", "FR-VLT-001")

    deal_id: Uuid = Field(description="Deal created by the import.")
    export_digest: Sha256Hex = Field(description="SHA-256 of the raw export file bytes.")
    file_name: str = Field(description="File name of the export as given by the user.")
    message_count: int = Field(ge=0, le=MAX_SAFE_INTEGER, description="Messages parsed.")
    imported_at: Timestamp = Field(description="Device-clock time of the import.")


class LeafRow(FrozenContractModel):
    """One row of leaves.jsonl in a receipt bundle. A disclosed leaf has its salt and payload
    digest; an undisclosed leaf has only its leaf hash (selective disclosure, P1).

    Requirements: FR-VLT-001, FR-VLT-002, FR-SEL-001.
    """

    model_config = requirements("FR-VLT-001", "FR-VLT-002", "FR-SEL-001")

    seq: int = Field(ge=1, le=MAX_SAFE_INTEGER, description="Position in the Merkle tree, from 1.")
    leaf_type: LeafType = Field(description="Which salted record type this leaf is.")
    leaf_hash: Sha256Hex = Field(description="The leaf hash.")
    salt: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")] | None = Field(
        description="The 16-byte salt as hex, or null if the leaf is not disclosed."
    )
    payload_digest: Sha256Hex | None = Field(
        description="Digest of the payload, or null if not disclosed."
    )
    payload: str | None = Field(
        description="Canonical JSON text of the record (not for audio or attachments), or null."
    )

    @model_validator(mode="after")
    def all_or_nothing(self) -> "LeafRow":
        disclosed = [self.salt is not None, self.payload_digest is not None]
        if any(disclosed) != all(disclosed):
            raise ValueError("salt and payload_digest are given together or not at all")
        if self.payload is not None and self.salt is None:
            raise ValueError("a payload needs its salt and digest")
        return self


class BundleFile(FrozenContractModel):
    """One file listed in a receipt bundle manifest.

    Requirements: FR-VFY-001.
    """

    model_config = requirements("FR-VFY-001")

    path: str = Field(description="Relative path inside the bundle.")
    role: BundleFileRole = Field(description="What the file is for.")
    sha256: Sha256Hex = Field(description="SHA-256 of the file bytes.")


class ReceiptBundle(FrozenContractModel):
    """The manifest of a receipt bundle (.zip): receipt.json, leaves.jsonl, chain.json, optional
    media and README.txt (INTEGRITY_SPEC section 9).

    Requirements: FR-VLT-002, FR-VFY-001, FR-DSP-001.
    """

    model_config = requirements("FR-VLT-002", "FR-VFY-001", "FR-DSP-001")

    spec_version: str = Field(description="Version of docs/INTEGRITY_SPEC.md that was followed.")
    deal_id: Uuid = Field(description="Deal the bundle covers.")
    files: tuple[BundleFile, ...] = Field(description="Every file in the bundle.")
    created_at: Timestamp = Field(description="When the bundle was written.")
