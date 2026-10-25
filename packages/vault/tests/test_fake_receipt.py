"""Tests for the demo-only fake receipt (issue #21). Written before the code.

Positive cases need the shared contracts (PR #40) and skip until they are merged; the
unavailable path runs everywhere.
"""

import json
from typing import Any

import pytest

from packages.integrity import receipt_hash, to_hex
from packages.vault import fake_receipt as fake


def contracts() -> Any:
    module = pytest.importorskip("packages.contracts", reason="Requires contracts PR #40")
    if not hasattr(module, "Receipt"):
        pytest.skip("Requires contracts PR #40")
    return module


def dumped(deal_id: str = "deal-demo") -> dict[str, Any]:
    data: dict[str, Any] = fake.fake_receipt(deal_id).model_dump(mode="json")
    return data


def test_fake_receipt_is_a_valid_contract_receipt() -> None:
    c = contracts()
    receipt = fake.fake_receipt("deal-demo")
    assert isinstance(receipt, c.Receipt)
    c.Receipt.model_validate_json(json.dumps(dumped()))


def test_fake_receipt_is_labelled_fake_with_fixed_hashes() -> None:
    contracts()
    data = dumped()
    assert data["spec_version"] == fake.FAKE_SPEC_VERSION
    assert "fake" in fake.FAKE_SPEC_VERSION and "not-verifiable" in fake.FAKE_SPEC_VERSION
    assert data["root"] == fake.FAKE_ROOT
    assert data["receipt_hash"] == fake.FAKE_RECEIPT_HASH
    assert fake.FAKE_ROOT != fake.FAKE_RECEIPT_HASH
    assert data["chain"] == [] and data["anchor"] is None and data["leaf_count"] == 1


def test_fake_receipt_is_deterministic_and_keeps_the_deal_id() -> None:
    contracts()
    assert dumped("deal-a") == dumped("deal-a")
    assert dumped("deal-b")["deal_id"] == "deal-b"


def test_fake_receipt_can_never_verify() -> None:
    """Its receipt_hash is not the real hash of its own fields, so no verifier accepts it."""
    contracts()
    data = dumped()
    listed = data.pop("receipt_hash")
    assert to_hex(receipt_hash(data)) != listed


def test_without_contracts_the_fake_receipt_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing(name: str) -> Any:
        raise ImportError(name)

    monkeypatch.setattr(fake, "import_module", missing)
    with pytest.raises(fake.FakeReceiptUnavailable):
        fake.fake_receipt("deal-demo")
