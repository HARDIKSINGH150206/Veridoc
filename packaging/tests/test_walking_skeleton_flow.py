"""One offline end-to-end test of the walking skeleton (issues #29 to #32).

Import a sample chat, get terms with source links, confirm terms the way the screen does (its own
JavaScript logic builds the request), get a recap with an echo code, record, and check the hashes
twice: in Python here and with the JavaScript primitives of apps/verify. No network is used.
"""

import json
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.settings import Settings
from packages.contracts import MessageSourceRef, Recap, Receipt, Term
from packages.integrity import (
    PREFIXES,
    JsonValue,
    derive_echo_code,
    leaf_hash,
    merkle_root,
    payload_digest,
    recap_hash,
    receipt_hash,
    to_hex,
)

ROOT = Path(__file__).resolve().parents[2]
WEB_TESTS = ROOT / "apps" / "web" / "tests"


def node(script: str, payload: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which("node")
    assert executable is not None, "Node.js is needed for the end-to-end test (CI has it)"
    done = subprocess.run(
        [executable, str(WEB_TESTS / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    result: dict[str, Any] = json.loads(done.stdout)
    return result


@pytest.fixture
def offline(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    def no_network(*args: object, **kwargs: object) -> None:
        pytest.fail("The end-to-end flow must not use the network")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "getaddrinfo", no_network)
    return tmp_path


def walk(api: TestClient) -> dict[str, Any]:
    names = api.get("/api/ingest/samples").json()["samples"]
    assert "clean" in names
    sample = api.get("/api/ingest/samples/clean").json()
    terms = api.get("/api/analysis/samples/clean/terms").json()
    assert terms["demo"] is True
    return {"sample": sample, "terms": terms["terms"]}


def test_import_to_verified_receipt_offline(offline: Path) -> None:
    with TestClient(create_app(Settings(demo_mode=True, model_mode="fake"))) as api:
        found = walk(api)
        sample, ai_terms = found["sample"], found["terms"]
        messages = sample["messages"]

        # Terms: unconfirmed, AI-proposed, every source a real message of the chat.
        parsed = [Term.model_validate_json(json.dumps(t)) for t in ai_terms]
        by_id = {m["id"]: m for m in messages}
        for term in parsed:
            assert term.confirmed_at is None and term.origin.value == "ai"
            for source in term.sources:
                assert isinstance(source, MessageSourceRef) and source.message_id in by_id

        # The screen's own logic decides what can be confirmed and builds the request.
        at = "2026-10-25T11:00:00+05:30"
        screen = node(
            "drive_skeleton.mjs",
            {
                "terms": ai_terms,
                "messages": messages,
                "participants": sample["participants"],
                "at": at,
            },
        )
        view = {v["key"]: v for v in screen["view"]}
        assert view["unit_price"]["status"] == {"cls": "clear", "word": "Clear"}
        assert view["quality_spec"]["status"] == {"cls": "missing", "word": "Missing"}
        assert view["delivery_date"]["confirmable"] is False, "a date without a year"
        assert view["unit_price"]["sources"] == ["#1"]
        confirmable = {k for k, v in view.items() if v["confirmable"]}
        assert {"unit_price", "total_amount", "advance_amount", "quantity", "buyer"} <= confirmable
        agreed = screen["agreed"]
        assert {a["key"] for a in agreed} == confirmable

        # Recap with an echo code.
        recap_response = api.post("/api/agreement/samples/clean/recap", json={"terms": agreed})
        assert recap_response.status_code == 200
        recap = Recap.model_validate_json(recap_response.text)
        assert recap.text.endswith(f"CONFIRM {recap.echo_code.code}")

        # Receipt.
        record_response = api.post("/api/vault/samples/clean/record", json={"terms": agreed})
        assert record_response.status_code == 200
        record = record_response.json()
        receipt = Receipt.model_validate_json(json.dumps(record["receipt"]))
        assert record["demo"] is True and "demo" in receipt.body.spec_version

        # Checked in Python ...
        leaves = []
        for row in record["leaf_rows"]:
            digest = payload_digest(row["payload"].encode())
            leaf = leaf_hash(PREFIXES["MESSAGE"], bytes.fromhex(row["salt"]), digest)
            assert to_hex(leaf) == row["leaf_hash"]
            leaves.append(leaf)
        assert to_hex(merkle_root(leaves)) == receipt.body.root
        assert to_hex(receipt_hash(record["receipt"]["body"])) == receipt.receipt_hash
        content: dict[str, JsonValue] = {
            "deal_id": recap.deal_id,
            "version_n": recap.version_n,
            "language": recap.language.value,
            "lines": [line.model_dump(mode="json") for line in recap.lines],
            "body_text": recap.body_text,
        }
        assert derive_echo_code(recap_hash(content)) == recap.echo_code.code

        # ... and again with the JavaScript primitives.
        checks = node(
            "verify_record.mjs", {"record": record, "recap": recap.model_dump(mode="json")}
        )
        assert checks == dict.fromkeys(checks, True), checks

        # Tamper-evidence: one changed character in a message makes the JavaScript check fail.
        record["leaf_rows"][0]["payload"] = record["leaf_rows"][0]["payload"].replace(
            "200", "300", 1
        )
        tampered = node(
            "verify_record.mjs", {"record": record, "recap": recap.model_dump(mode="json")}
        )
        assert tampered["leaves"] is False

    assert not list(offline.iterdir()), "the flow must not write anything to disk"


def test_nothing_is_recorded_without_the_users_confirmation(offline: Path) -> None:
    with TestClient(create_app(Settings(demo_mode=True))) as api:
        found = walk(api)
        # The AI's own terms (no confirmation fields) are not accepted by the recap or the vault.
        for route in ("/api/agreement/samples/clean/recap", "/api/vault/samples/clean/record"):
            assert api.post(route, json={"terms": found["terms"]}).status_code == 422
            assert api.post(route, json={"terms": []}).status_code == 422
    assert not list(offline.iterdir())


def test_a_different_confirmed_term_gives_a_different_code(offline: Path) -> None:
    with TestClient(create_app(Settings(demo_mode=True))) as api:
        found = walk(api)
        at = "2026-10-25T11:00:00+05:30"
        agreed = node(
            "drive_skeleton.mjs",
            {
                "terms": found["terms"],
                "messages": found["sample"]["messages"],
                "participants": found["sample"]["participants"],
                "at": at,
            },
        )["agreed"]
        first = api.post("/api/agreement/samples/clean/recap", json={"terms": agreed}).json()
        fewer = api.post("/api/agreement/samples/clean/recap", json={"terms": agreed[1:]}).json()
    assert first["recap_hash"] != fewer["recap_hash"]
