"""Demo-only fake receipt for the walking skeleton (issue #21). Never real evidence.

Every hash is a fixed placeholder and spec_version says the receipt cannot be verified, so it can
never be mistaken for a real one. Nothing is read from or written to the vault, and no clock is
used. The real receipt is built from the vault's leaves and version chain (INTEGRITY_SPEC 9).
"""

from datetime import UTC, datetime
from importlib import import_module

from pydantic import BaseModel, ValidationError

FAKE_SPEC_VERSION = "demo-fake-not-verifiable"
FAKE_ROOT = "0" * 56 + "fa4e0001"
FAKE_RECEIPT_HASH = "0" * 56 + "fa4e0002"
FAKE_RECORDED_AT = datetime(2000, 1, 1, tzinfo=UTC)


class FakeReceiptUnavailable(Exception):
    """The shared Receipt contract is not available (contracts PR #40 not merged)."""


def fake_receipt(deal_id: str) -> BaseModel:
    """A Receipt for deal_id with fixed fake hashes, validated with the shared contract."""
    # STUB: replaced by #31 (walking-skeleton integration); the real receipt follows in Phase 3.
    try:
        # Resolved lazily so dev still starts before contracts PR #40 is merged.
        model = import_module("packages.contracts").Receipt
        if not isinstance(model, type) or not issubclass(model, BaseModel):
            raise TypeError
        receipt: BaseModel = model.model_validate(
            {
                "spec_version": FAKE_SPEC_VERSION,
                "deal_id": deal_id,
                "leaf_count": 1,
                "root": FAKE_ROOT,
                "chain": (),
                "recorded_at": FAKE_RECORDED_AT,
                "anchor": None,
                "receipt_hash": FAKE_RECEIPT_HASH,
            }
        )
    except (ImportError, AttributeError, TypeError, ValidationError):
        raise FakeReceiptUnavailable("Receipt contract unavailable") from None
    return receipt
