"""#16 / NFR-MNT-002: real sample import, test-only analysis and record adapters.

This is a contract-flow harness, not proof that the four-area UI is wired.
"""

import hashlib
import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from apps.api.main import create_app
from apps.api.settings import Settings

Adapters = tuple[
    Callable[[list[dict[str, object]]], BaseModel],
    Callable[[list[dict[str, object]], BaseModel], BaseModel],
]


@pytest.fixture
def skeleton_adapters() -> Adapters:
    contracts = pytest.importorskip("packages.contracts", reason="Requires contracts PR #40")
    if not hasattr(contracts, "Term"):
        pytest.skip("Requires contracts PR #40")

    # STUB: replaced by #30 (Abhishek's analysis adapter).
    def analyze(messages: list[dict[str, object]]) -> BaseModel:
        first = messages[0]
        payload = {
            "id": "test-term",
            "deal_id": first["deal_id"],
            "key": "scope",
            "value_type": "text",
            "value": first["text"],
            "unit": None,
            "raw": first["text"],
            "state": "clear",
            "origin": "ai",
            "confidence": "low",
            "needs_review": True,
            "sources": [{"kind": "message", "message_id": first["id"], "quote": first["text"]}],
            "alternatives": [],
            "confirmed_at": None,
            "acknowledged_by_other": False,
        }
        result: BaseModel = contracts.Term.model_validate_json(json.dumps(payload))
        return result

    # STUB: replaced by #31 (Area 3's record adapter).
    def record(messages: list[dict[str, object]], term: BaseModel) -> BaseModel:
        values = term.model_dump(mode="json")
        if values["confirmed_at"] is None:
            raise ValueError("Human confirmation required")
        assert values["deal_id"] == messages[0]["deal_id"]
        # Computed sentinel, NOT a Merkle root or a canonical receipt hash.
        fake_digest = hashlib.sha256(b"test-only-fake-not-verifiable").hexdigest()
        payload = {
            "spec_version": "test-only-fake-not-verifiable",
            "deal_id": values["deal_id"],
            "leaf_count": len(messages),
            "root": fake_digest,
            "chain": [],
            "recorded_at": values["confirmed_at"],
            "anchor": None,
            "receipt_hash": fake_digest,
        }
        result: BaseModel = contracts.Receipt.model_validate_json(json.dumps(payload))
        return result

    return analyze, record


def test_import_to_confirmed_fake_receipt(
    skeleton_adapters: Adapters, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    contracts = pytest.importorskip("packages.contracts", reason="Requires contracts PR #40")
    if not hasattr(contracts, "Message"):
        pytest.skip("Requires contracts PR #40")
    analyze, record = skeleton_adapters
    with TestClient(create_app(Settings(demo_mode=True))) as api:
        response = api.get("/api/ingest/samples/clean/messages")
    assert response.status_code == 200
    messages = response.json()
    for message in messages:
        contracts.Message.model_validate_json(json.dumps(message))
    proposed = analyze(messages)
    term = proposed.model_dump(mode="json")
    assert term["confirmed_at"] is None
    assert term["sources"][0]["message_id"] == messages[0]["id"]
    with pytest.raises(ValueError, match="Human confirmation required"):
        record(messages, proposed)
    # Simulated explicit human action in a test, never AI auto-confirmation.
    term["confirmed_at"] = messages[-1]["ts"]
    confirmed = contracts.Term.model_validate_json(json.dumps(term))
    receipt = record(messages, confirmed).model_dump(mode="json")
    contracts.Receipt.model_validate_json(json.dumps(receipt))
    assert receipt["deal_id"] == messages[0]["deal_id"]
    assert receipt["leaf_count"] == len(messages)
    assert receipt["spec_version"] == "test-only-fake-not-verifiable"
    assert receipt["anchor"] is None
    assert datetime.fromisoformat(receipt["recorded_at"]).tzinfo is not None
    assert not list(tmp_path.iterdir()), "The harness must not write vault records"
