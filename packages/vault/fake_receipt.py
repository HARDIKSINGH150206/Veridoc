"""Demo-only fake receipt for the walking skeleton (issue #21). Never real evidence.

Every hash is a fixed placeholder and spec_version says the receipt cannot be verified, so it can
never be mistaken for a real one. Nothing is read from or written to the vault, and no clock is
used. The real receipt is built from the vault's leaves and version chain (INTEGRITY_SPEC 9) and is
an envelope: the body, and the hash of the body held outside it.
"""

from datetime import UTC, datetime

from packages.contracts import Receipt, ReceiptBody

FAKE_SPEC_VERSION = "demo-fake-not-verifiable"
FAKE_ROOT = "0" * 56 + "fa4e0001"
FAKE_RECEIPT_HASH = "0" * 56 + "fa4e0002"
FAKE_RECORDED_AT = datetime(2000, 1, 1, tzinfo=UTC)


def fake_receipt(deal_id: str) -> Receipt:
    """A Receipt envelope for deal_id (a UUID) with fixed fake hashes, in the shared contract."""
    # STUB: replaced by #31 (walking-skeleton integration); the real receipt follows in Phase 3.
    body = ReceiptBody(
        spec_version=FAKE_SPEC_VERSION,
        deal_id=deal_id,
        leaf_count=1,
        root=FAKE_ROOT,
        chain=(),
        recorded_at=FAKE_RECORDED_AT,
        anchor=None,
    )
    return Receipt(body=body, receipt_hash=FAKE_RECEIPT_HASH)
