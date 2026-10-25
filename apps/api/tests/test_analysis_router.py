"""Demo analysis route (issue #30)."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings
from packages.contracts import Term

ROUTE = "/api/analysis/samples/{name}/terms"


def client(demo: bool = True, mode: str = "fake") -> TestClient:
    return TestClient(create_app(Settings(demo_mode=demo, model_mode=mode)))  # type: ignore[arg-type]


def test_hidden_outside_demo_mode() -> None:
    with client(demo=False) as api:
        assert api.get(ROUTE.format(name="clean")).status_code == 404


@pytest.mark.parametrize("name", ["clean", "ambiguous", "contradictory"])
def test_terms_come_back_as_contract_terms(name: str) -> None:
    with client() as api:
        response = api.get(ROUTE.format(name=name))
    assert response.status_code == 200
    body = response.json()
    assert body["demo"] is True
    terms = [Term.model_validate_json(json.dumps(t)) for t in body["terms"]]
    assert len(terms) == 11 and all(t.confirmed_at is None for t in terms)


def test_unknown_sample_is_404() -> None:
    with client() as api:
        assert api.get(ROUTE.format(name="nope")).status_code == 404


def test_local_mode_is_not_built_and_says_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with client(mode="local") as api:
        response = api.get(ROUTE.format(name="clean"))
    assert response.status_code == 501
    assert "VERIDOC_MODEL_MODE" in response.json()["detail"]
    assert not list(tmp_path.iterdir())
