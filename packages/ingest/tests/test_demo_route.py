"""Demo ingest boundary for #14: FR-IMP-007, FR-IMP-009."""

import json
import os
import socket
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "messages"


@pytest.fixture(autouse=True)
def isolate_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    for name in os.environ:
        if name.startswith("VERIDOC_"):
            monkeypatch.delenv(name)


def client(demo: bool) -> TestClient:
    return TestClient(create_app(Settings(demo_mode=demo)))


def test_demo_disabled() -> None:
    with client(False) as api:
        assert api.get("/api/ingest/samples/clean/messages").status_code == 404


@pytest.mark.parametrize("sample", ("clean", "ambiguous", "contradictory"))
def test_demo_returns_validated_fixture(sample: str, monkeypatch: pytest.MonkeyPatch) -> None:
    chat = pytest.importorskip("packages.contracts.chat", reason="Requires contracts PR #40")

    def no_network(*args: object, **kwargs: object) -> None:
        pytest.fail("Demo import must not connect to the network")

    # Windows asyncio needs a loopback socket pair to start its event loop.
    # Block networking only while the in-process request is being served.
    with client(True) as api, monkeypatch.context() as guard:
        guard.setattr(socket.socket, "connect", no_network)
        guard.setattr(socket, "getaddrinfo", no_network)
        response = api.get(f"/api/ingest/samples/{sample}/messages")
    assert response.status_code == 200
    assert response.json() == json.loads((FIXTURES / f"{sample}.json").read_text("utf-8"))
    for message in response.json():
        chat.Message.model_validate_json(json.dumps(message))


def test_missing_contract_returns_safe_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    from packages.ingest import samples

    def missing(name: str) -> object:
        raise ModuleNotFoundError("private path must not escape")

    monkeypatch.setattr(samples, "import_module", missing)
    with client(True) as api:
        response = api.get("/api/ingest/samples/clean/messages")
        assert response.status_code == 503
        assert "private" not in response.text
        assert api.get("/api/health").status_code == 200


@pytest.mark.parametrize("sample", ("unknown", "clean.json", "%2e%2e", "%2e%2e%2fclean"))
def test_unknown_or_path_input_rejected(sample: str) -> None:
    with client(True) as api:
        assert api.get(f"/api/ingest/samples/{sample}/messages").status_code == 404


def test_corrupt_fixture_fails_closed(tmp_path: Path) -> None:
    pytest.importorskip("packages.contracts.chat", reason="Requires contracts PR #40")
    from packages.ingest.samples import SampleUnavailable, load_messages

    (tmp_path / "broken.json").write_text('[{"text":"private"}]', encoding="utf-8")
    with pytest.raises(SampleUnavailable, match="Sample data unavailable"):
        load_messages("broken", tmp_path)
