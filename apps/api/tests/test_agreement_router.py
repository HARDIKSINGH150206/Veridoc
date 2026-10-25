"""Demo recap route (issue #29): confirmed terms in, recap with echo code out."""

import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings
from packages.contracts import Recap
from packages.ingest.samples import load_sample

FIXTURES = Path(__file__).resolve().parents[3] / "packages" / "ingest" / "fixtures"
ROUTE = "/api/agreement/samples/clean/recap"


def client(demo: bool) -> TestClient:
    return TestClient(create_app(Settings(demo_mode=demo)))


def confirmed(key: str = "total_amount", paise: str = "9600000") -> dict[str, Any]:
    sample = load_sample("clean", FIXTURES)
    me = next(p.id for p in sample.participants if p.is_me)
    return {
        "key": key,
        "value": {"kind": "money", "paise": paise},
        "sources": [{"kind": "message", "message_id": sample.messages[0].id, "quote": None}],
        "confirmed_by": me,
        "confirmed_at": "2026-10-25T11:00:00+05:30",
    }


def test_hidden_outside_demo_mode() -> None:
    with client(False) as api:
        assert api.post(ROUTE, json={"terms": [confirmed()]}).status_code == 404


def test_confirmed_terms_give_a_recap_with_an_echo_code() -> None:
    with client(True) as api:
        response = api.post(ROUTE, json={"terms": [confirmed()]})
    assert response.status_code == 200
    recap = Recap.model_validate_json(json.dumps(response.json()))
    assert recap.version_n == 1 and recap.text.endswith(f"CONFIRM {recap.echo_code.code}")
    assert recap.deal_id == load_sample("clean", FIXTURES).messages[0].deal_id


def test_the_same_confirmed_terms_give_the_same_code() -> None:
    with client(True) as api:
        first = api.post(ROUTE, json={"terms": [confirmed()]}).json()
        second = api.post(ROUTE, json={"terms": [confirmed()]}).json()
        changed = api.post(ROUTE, json={"terms": [confirmed(paise="9700000")]}).json()
    assert first["echo_code"] == second["echo_code"] != changed["echo_code"]


def test_no_terms_is_rejected_and_nothing_is_written(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.chdir(tmp_path)
    with client(True) as api:
        assert api.post(ROUTE, json={"terms": []}).status_code == 422
        assert api.post(ROUTE, json={}).status_code == 422
    assert not list(tmp_path.iterdir())


def test_terms_not_confirmed_by_the_user_or_without_real_sources_are_rejected() -> None:
    bad_user = {**confirmed(), "confirmed_by": "00000000-0000-4000-8000-000000000000"}
    bad_source = confirmed()
    bad_source["sources"][0]["message_id"] = "00000000-0000-4000-8000-000000000000"
    with client(True) as api:
        assert api.post(ROUTE, json={"terms": [bad_user]}).status_code == 422
        assert api.post(ROUTE, json={"terms": [bad_source]}).status_code == 422


def test_a_term_still_missing_confirmation_fields_is_rejected() -> None:
    unconfirmed = confirmed()
    unconfirmed["confirmed_at"] = None
    with client(True) as api:
        assert api.post(ROUTE, json={"terms": [unconfirmed]}).status_code == 422


def test_unknown_sample_is_404() -> None:
    with client(True) as api:
        assert (
            api.post("/api/agreement/samples/nope/recap", json={"terms": [confirmed()]}).status_code
            == 404
        )
