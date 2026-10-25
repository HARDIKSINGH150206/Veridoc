"""Tests for the vault router's demo receipt route (issue #21). Written before the code."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings
from packages.vault import fake_receipt as fake

ROUTE = "/api/vault/deals/{deal_id}/receipt"


def client(demo_mode: bool) -> TestClient:
    return TestClient(create_app(Settings(demo_mode=demo_mode)))


def test_the_route_is_loaded_by_auto_discovery() -> None:
    assert ROUTE in create_app(Settings()).openapi()["paths"]


def test_outside_demo_mode_the_route_does_not_exist() -> None:
    with client(demo_mode=False) as api:
        response = api.get(ROUTE.format(deal_id="deal-demo"))
    assert response.status_code == 404


def test_an_unsafe_deal_id_is_rejected() -> None:
    with client(demo_mode=True) as api:
        for bad in ("a" * 65, "deal%20one", "deal.json"):
            assert api.get(ROUTE.format(deal_id=bad)).status_code in {404, 422}


def test_without_contracts_demo_mode_answers_503(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(name: str) -> Any:
        raise ImportError(name)

    monkeypatch.setattr(fake, "import_module", missing)
    with client(demo_mode=True) as api:
        response = api.get(ROUTE.format(deal_id="deal-demo"))
    assert response.status_code == 503
    assert "deal-demo" not in response.text


def test_demo_mode_returns_the_labelled_fake_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contracts = pytest.importorskip("packages.contracts", reason="Requires contracts PR #40")
    if not hasattr(contracts, "Receipt"):
        pytest.skip("Requires contracts PR #40")
    monkeypatch.chdir(tmp_path)
    with client(demo_mode=True) as api:
        response = api.get(ROUTE.format(deal_id="deal-demo"))
    assert response.status_code == 200
    body = response.json()
    contracts.Receipt.model_validate_json(json.dumps(body))
    assert body["deal_id"] == "deal-demo"
    assert body["spec_version"] == fake.FAKE_SPEC_VERSION
    assert body["receipt_hash"] == fake.FAKE_RECEIPT_HASH
    assert not list(tmp_path.iterdir()), "the demo receipt must not write anything"
