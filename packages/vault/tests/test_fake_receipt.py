"""Tests for the demo-only fake receipt (issue #21), against contracts v0.2.0."""

import json
from typing import Any

import pytest

from packages.contracts import Receipt
from packages.integrity import receipt_hash, to_hex
from packages.vault import fake_receipt as fake

DEAL_A = "11111111-1111-4111-8111-111111111111"
DEAL_B = "22222222-2222-4222-8222-222222222222"


def dumped(deal_id: str = DEAL_A) -> dict[str, Any]:
    data: dict[str, Any] = fake.fake_receipt(deal_id).model_dump(mode="json")
    return data


def test_fake_receipt_is_a_valid_contract_receipt_envelope() -> None:
    receipt = fake.fake_receipt(DEAL_A)
    assert isinstance(receipt, Receipt)
    Receipt.model_validate_json(json.dumps(dumped()))
    assert set(dumped()) == {"body", "receipt_hash"}


def test_fake_receipt_is_labelled_fake_with_fixed_hashes() -> None:
    data = dumped()
    body = data["body"]
    assert body["spec_version"] == fake.FAKE_SPEC_VERSION
    assert "fake" in fake.FAKE_SPEC_VERSION and "not-verifiable" in fake.FAKE_SPEC_VERSION
    assert body["root"] == fake.FAKE_ROOT
    assert data["receipt_hash"] == fake.FAKE_RECEIPT_HASH
    assert fake.FAKE_ROOT != fake.FAKE_RECEIPT_HASH
    assert body["chain"] == [] and body["anchor"] is None and body["leaf_count"] == 1


def test_fake_receipt_is_deterministic_and_keeps_the_deal_id() -> None:
    assert dumped(DEAL_A) == dumped(DEAL_A)
    assert dumped(DEAL_B)["body"]["deal_id"] == DEAL_B


def test_fake_receipt_can_never_verify() -> None:
    """Its receipt_hash is not the real hash of its own body, so no verifier accepts it."""
    data = dumped()
    assert to_hex(receipt_hash(data["body"])) != data["receipt_hash"]


def test_a_deal_id_that_is_not_a_uuid_is_rejected() -> None:
    with pytest.raises(ValueError):
        fake.fake_receipt("deal-demo")
