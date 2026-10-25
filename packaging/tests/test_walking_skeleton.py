"""#16 / NFR-MNT-002: real sample import, test-only analysis and record adapters.

This is a contract-flow harness, not proof that the four-area UI is wired.
"""

import hashlib
import json
import uuid
from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings
from packages.contracts import Message, MessageSourceRef, Receipt, ReceiptBody, Term

Adapters = tuple[
    Callable[[list[dict[str, object]]], Term],
    Callable[[list[dict[str, object]], Term], Receipt],
]


@pytest.fixture
def skeleton_adapters() -> Adapters:
    # STUB: replaced by #30 (Abhishek's analysis adapter).
    def analyze(messages: list[dict[str, object]]) -> Term:
        first = messages[0]
        payload = {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, "skeleton-term")),
            "deal_id": first["deal_id"],
            "key": "scope",
            "value": {"kind": "text", "text": first["text"]},
            "raw": first["text"],
            "state": "stated",
            "unclear_reason": None,
            "origin": "ai",
            "confidence": "low",
            "needs_review": True,
            "sources": [{"kind": "message", "message_id": first["id"], "quote": first["text"]}],
            "alternatives": [],
            "confirmed_at": None,
            "confirmed_by": None,
            "acknowledged_by_other": False,
        }
        return Term.model_validate_json(json.dumps(payload))

    # STUB: replaced by #31 (Area 3's record adapter).
    def record(messages: list[dict[str, object]], term: Term) -> Receipt:
        if term.confirmed_at is None:
            raise ValueError("Human confirmation required")
        assert str(term.deal_id) == messages[0]["deal_id"]
        # Computed sentinel, NOT a Merkle root or a canonical receipt hash.
        fake_digest = hashlib.sha256(b"test-only-fake-not-verifiable").hexdigest()
        body = ReceiptBody(
            spec_version="test-only-fake-not-verifiable",
            deal_id=term.deal_id,
            leaf_count=len(messages),
            root=fake_digest,
            chain=(),
            recorded_at=term.confirmed_at,
            anchor=None,
        )
        return Receipt(body=body, receipt_hash=fake_digest)

    return analyze, record


def test_import_to_confirmed_fake_receipt(
    skeleton_adapters: Adapters, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    analyze, record = skeleton_adapters
    with TestClient(create_app(Settings(demo_mode=True))) as api:
        response = api.get("/api/ingest/samples/clean/messages")
    assert response.status_code == 200
    messages = response.json()
    for message in messages:
        Message.model_validate_json(json.dumps(message))
    proposed = analyze(messages)
    assert proposed.confirmed_at is None
    source = proposed.sources[0]
    assert isinstance(source, MessageSourceRef)
    assert str(source.message_id) == messages[0]["id"]
    with pytest.raises(ValueError, match="Human confirmation required"):
        record(messages, proposed)
    # Simulated explicit human action in a test, never AI auto-confirmation.
    term = proposed.model_dump(mode="json")
    term["confirmed_at"] = messages[-1]["ts"]
    term["confirmed_by"] = messages[-1]["sender_id"]
    confirmed = Term.model_validate_json(json.dumps(term))
    receipt = record(messages, confirmed)
    Receipt.model_validate_json(receipt.model_dump_json())
    assert str(receipt.body.deal_id) == messages[0]["deal_id"]
    assert receipt.body.leaf_count == len(messages)
    assert receipt.body.spec_version == "test-only-fake-not-verifiable"
    assert receipt.body.anchor is None
    assert receipt.body.recorded_at.tzinfo is not None
    assert not list(tmp_path.iterdir()), "The harness must not write vault records"
