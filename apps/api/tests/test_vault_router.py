"""Tests for the vault router's demo receipt route (issue #21), against contracts v0.2.0."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings
from packages.contracts import Receipt
from packages.integrity import receipt_hash, to_hex
from packages.vault import fake_receipt as fake

ROUTE = "/api/vault/deals/{deal_id}/receipt"
DEAL = "11111111-1111-4111-8111-111111111111"


def client(demo_mode: bool) -> TestClient:
    return TestClient(create_app(Settings(demo_mode=demo_mode)))


def test_the_route_is_loaded_by_auto_discovery() -> None:
    assert ROUTE in create_app(Settings()).openapi()["paths"]


def test_outside_demo_mode_the_route_does_not_exist() -> None:
    with client(demo_mode=False) as api:
        response = api.get(ROUTE.format(deal_id=DEAL))
    assert response.status_code == 404


def test_a_deal_id_that_is_not_a_lowercase_uuid_is_rejected() -> None:
    with client(demo_mode=True) as api:
        for bad in (
            "deal-demo",
            "a" * 65,
            "deal%20one",
            "deal.json",
            "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA",
        ):
            assert api.get(ROUTE.format(deal_id=bad)).status_code in {404, 422}, bad


def test_demo_mode_returns_the_labelled_fake_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with client(demo_mode=True) as api:
        response = api.get(ROUTE.format(deal_id=DEAL))
    assert response.status_code == 200
    body = response.json()
    Receipt.model_validate_json(json.dumps(body))
    assert body["body"]["deal_id"] == DEAL
    assert body["body"]["spec_version"] == fake.FAKE_SPEC_VERSION
    assert body["receipt_hash"] == fake.FAKE_RECEIPT_HASH
    assert to_hex(receipt_hash(body["body"])) != body["receipt_hash"], "can never verify"
    assert not list(tmp_path.iterdir()), "the demo receipt must not write anything"
