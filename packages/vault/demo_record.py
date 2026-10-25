"""Demo record for the walking skeleton (issue #31). Pure: no I/O, no clock, salts passed in.

The hashes are the real ones from packages/integrity, computed over demo data, so the receipt
verifies by the steps of docs/INTEGRITY_SPEC.md section 10. It is labelled by its spec_version,
which no verifier supports, so it can never be mistaken for evidence. Only the message leaves are
recorded here; term, confirmation and other leaves come with the real vault (#57).
"""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from packages.contracts import (
    AgreedTerm,
    AgreementVersion,
    ChainLink,
    LeafRow,
    LeafType,
    Message,
    PlaybookRef,
    Receipt,
    ReceiptBody,
    Timestamp,
)
from packages.integrity import (
    PREFIXES,
    JsonValue,
    canonical_record,
    chain_links,
    leaf_hash,
    merkle_root,
    payload_digest,
    receipt_hash,
    terms_digest,
    to_hex,
)
from packages.integrity.hashing import SALT_SIZE

DEMO_SPEC_VERSION = "demo-skeleton-not-for-evidence"
FIRST_VERSION = 1
_NAMESPACE = uuid.UUID("9d4e6b1a-7c2f-4e83-b5a0-3f8d2c7e1a64")


class DemoRecordError(ValueError):
    """The input cannot be recorded."""


@dataclass(frozen=True)
class DemoRecord:
    version: AgreementVersion
    receipt: Receipt
    leaf_rows: tuple[LeafRow, ...]


def record_demo(
    messages: Sequence[Message],
    terms: Sequence[AgreedTerm],
    playbook: PlaybookRef,
    salts: Sequence[bytes],
    recorded_at: Timestamp,
) -> DemoRecord:
    """Leaves for the messages, one agreement version with its chain link, and the receipt."""
    if not messages or not terms:
        raise DemoRecordError("messages and confirmed terms are both needed")
    if len(salts) != len(messages) or any(len(s) != SALT_SIZE for s in salts):
        raise DemoRecordError("one 16-byte salt per message is needed")
    deal_id = messages[0].deal_id
    if any(m.deal_id != deal_id for m in messages):
        raise DemoRecordError("all messages must belong to one deal")
    if [m.seq for m in messages] != sorted(m.seq for m in messages):
        raise DemoRecordError("messages must be in sequence order")

    rows: list[LeafRow] = []
    leaves: list[bytes] = []
    for position, (message, salt) in enumerate(zip(messages, salts, strict=True), start=1):
        payload = canonical_record(message.model_dump(mode="json"))
        digest = payload_digest(payload)
        leaf = leaf_hash(PREFIXES["MESSAGE"], salt, digest)
        leaves.append(leaf)
        rows.append(
            LeafRow(
                seq=position,
                leaf_type=LeafType.MESSAGE,
                leaf_hash=to_hex(leaf),
                salt=salt.hex(),
                payload_digest=to_hex(digest),
                payload=payload.decode("utf-8"),
            )
        )
    root = merkle_root(leaves)

    ordered = tuple(sorted(terms, key=lambda t: t.key))
    terms_set: dict[str, JsonValue] = {
        "deal_id": deal_id,
        "version_n": FIRST_VERSION,
        "playbook": playbook.model_dump(mode="json"),
        "terms": [t.model_dump(mode="json") for t in ordered],
    }
    digest = terms_digest(terms_set)
    (link,) = chain_links([(digest, root)])
    version = AgreementVersion(
        id=str(uuid.uuid5(_NAMESPACE, f"{deal_id}:{FIRST_VERSION}")),
        deal_id=deal_id,
        version_n=FIRST_VERSION,
        playbook=playbook,
        terms=ordered,
        terms_digest=to_hex(digest),
        root=to_hex(root),
        link=to_hex(link),
        prev_link=None,
        reason_message_id=None,
        created_at=recorded_at,
    )
    body = ReceiptBody(
        spec_version=DEMO_SPEC_VERSION,
        deal_id=deal_id,
        leaf_count=len(leaves),
        root=to_hex(root),
        chain=(
            ChainLink(
                version_n=FIRST_VERSION,
                terms_digest=to_hex(digest),
                root=to_hex(root),
                link=to_hex(link),
            ),
        ),
        recorded_at=recorded_at,
        anchor=None,
    )
    receipt = Receipt(body=body, receipt_hash=to_hex(receipt_hash(body.model_dump(mode="json"))))
    return DemoRecord(version=version, receipt=receipt, leaf_rows=tuple(rows))
