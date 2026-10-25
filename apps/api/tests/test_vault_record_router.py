"""Demo record route (issue #31): confirmed terms in, a receipt over real hashes out."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings
from packages.contracts import AgreementVersion, LeafRow, Receipt
from packages.ingest.samples import load_sample
from packages.integrity import payload_digest, to_hex
from packages.vault.demo_record import DEMO_SPEC_VERSION

FIXTURES = Path(__file__).resolve().parents[3] / "packages" / "ingest" / "fixtures"
ROUTE = "/api/vault/samples/clean/record"


def client(demo: bool) -> TestClient:
    return TestClient(create_app(Settings(demo_mode=demo)))


def confirmed(paise: str = "9600000") -> dict[str, Any]:
    sample = load_sample("clean", FIXTURES)
    me = next(p.id for p in sample.participants if p.is_me)
    return {
        "key": "total_amount",
        "value": {"kind": "money", "paise": paise},
        "sources": [{"kind": "message", "message_id": sample.messages[0].id, "quote": None}],
        "confirmed_by": me,
        "confirmed_at": "2026-10-25T11:00:00+05:30",
    }


def test_hidden_outside_demo_mode() -> None:
    with client(False) as api:
        assert api.post(ROUTE, json={"terms": [confirmed()]}).status_code == 404


def test_confirmed_terms_give_a_labelled_receipt_with_real_hashes() -> None:
    with client(True) as api:
        response = api.post(ROUTE, json={"terms": [confirmed()]})
    assert response.status_code == 200
    body = response.json()
    assert body["demo"] is True
    receipt = Receipt.model_validate_json(json.dumps(body["receipt"]))
    AgreementVersion.model_validate_json(json.dumps(body["version"]))
    rows = [LeafRow.model_validate_json(json.dumps(r)) for r in body["leaf_rows"]]
    sample = load_sample("clean", FIXTURES)
    assert receipt.body.spec_version == DEMO_SPEC_VERSION
    assert len(rows) == receipt.body.leaf_count == len(sample.messages)
    for row in rows:
        assert row.payload is not None
        assert to_hex(payload_digest(row.payload.encode())) == row.payload_digest


def test_every_record_uses_fresh_salts() -> None:
    with client(True) as api:
        first = api.post(ROUTE, json={"terms": [confirmed()]}).json()
        second = api.post(ROUTE, json={"terms": [confirmed()]}).json()
    assert first["receipt"]["body"]["root"] != second["receipt"]["body"]["root"]
    assert {r["salt"] for r in first["leaf_rows"]}.isdisjoint(
        {r["salt"] for r in second["leaf_rows"]}
    )


@pytest.mark.parametrize(
    "body",
    [{}, {"terms": []}, {"terms": "x"}, {"terms": [{"key": "a"}]}, {"terms": [], "extra": 1}],
)
def test_bad_bodies_are_rejected_without_writing(
    body: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with client(True) as api:
        response = api.post(ROUTE, json=body)
    assert response.status_code == 422
    assert not list(tmp_path.iterdir())
    assert "total_amount" not in response.text


def test_terms_not_confirmed_by_the_user_are_rejected() -> None:
    bad = {**confirmed(), "confirmed_by": "00000000-0000-4000-8000-000000000000"}
    with client(True) as api:
        assert api.post(ROUTE, json={"terms": [bad]}).status_code == 422


def test_an_unconfirmed_term_cannot_be_recorded() -> None:
    bad = {**confirmed(), "confirmed_at": None}
    with client(True) as api:
        assert api.post(ROUTE, json={"terms": [bad]}).status_code == 422


def test_the_existing_fake_receipt_route_is_unchanged() -> None:
    with client(True) as api:
        response = api.get("/api/vault/deals/11111111-1111-4111-8111-111111111111/receipt")
    assert response.status_code == 200
