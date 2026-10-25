"""The sample deals in packages/contracts/fixtures/ validate against the models, and the hashes
inside them are the ones packages/integrity computes from the fixture data."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, TypeAdapter

import packages.contracts as c
from packages.integrity import (
    PREFIXES,
    canonical_record,
    chain_links,
    derive_echo_code,
    from_hex,
    merkle_root,
    recap_hash,
    receipt_hash,
    record_leaf,
    sha256,
    terms_digest,
    to_hex,
)

FIXTURES = Path(c.__file__).resolve().parent / "fixtures"
DEALS = sorted(FIXTURES.glob("*.deal.json"))
SECTIONS: dict[str, type[BaseModel]] = {
    "participants": c.Participant,
    "messages": c.Message,
    "voice_notes": c.VoiceNote,
    "transcripts": c.Transcript,
    "terms": c.Term,
    "flags": c.Flag,
    "suggestions": c.Suggestion,
    "handshake_questions": c.HandshakeQuestion,
    "sealed_answers": c.SealedAnswers,
    "handshake_reveals": c.HandshakeReveal,
    "recaps": c.Recap,
    "confirmations": c.Confirmation,
    "versions": c.AgreementVersion,
    "version_diffs": c.VersionDiff,
    "receipts": c.Receipt,
    "verify_results": c.VerifyResult,
    "dispute_packs": c.DisputePackManifest,
    "import_records": c.ImportRecord,
    "leaf_rows": c.LeafRow,
    "bundles": c.ReceiptBundle,
}


def load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def parsed(path: Path) -> dict[str, list[Any]]:
    data = load(path)
    out: dict[str, list[Any]] = {
        name: [model.model_validate_json(json.dumps(item)) for item in data[name]]
        for name, model in SECTIONS.items()
    }
    out["score"] = [c.EvidenceScore.model_validate_json(json.dumps(data["score"]))]
    out["playbook"] = [c.PlaybookRef.model_validate_json(json.dumps(data["playbook"]))]
    return out


def terms_set(version: c.AgreementVersion) -> Any:
    """The hashed content of a version: INTEGRITY_SPEC section 4, agreed-terms set."""
    return {
        "deal_id": version.deal_id,
        "version_n": version.version_n,
        "playbook": dump(version.playbook),
        "terms": [dump(t) for t in sorted(version.terms, key=lambda t: t.key)],
    }


def dump(model: BaseModel) -> Any:
    return model.model_dump(mode="json")


def test_the_sample_files_exist() -> None:
    assert [p.name for p in DEALS] == [
        "ambiguous.deal.json",
        "clean.deal.json",
        "contradictory.deal.json",
    ]
    assert (FIXTURES / "api.sample.json").is_file()


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_every_section_validates_against_its_model(path: Path) -> None:
    assert parsed(path)


def test_api_samples_validate() -> None:
    data = load(FIXTURES / "api.sample.json")
    envelopes = [c.StreamEnvelope.model_validate_json(json.dumps(e)) for e in data["stream_events"]]
    assert [e.event_id for e in envelopes] == list(range(1, len(envelopes) + 1))
    assert {e.event.type for e in envelopes} == {
        "term", "flag", "score", "suggestion", "progress", "done", "error",
    }  # fmt: skip
    c.ErrorBody.model_validate_json(json.dumps(data["error_body"]))
    summaries = [c.DealSummary.model_validate_json(json.dumps(s)) for s in data["deal_summaries"]]
    assert len(summaries) == 3


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_ids_referenced_by_sources_exist(path: Path) -> None:
    data = load(path)
    message_ids = {m["id"] for m in data["messages"]}
    voice_ids = {v["id"] for v in data["voice_notes"]}
    participant_ids = {p["id"] for p in data["participants"]}

    def check(sources: list[dict[str, Any]]) -> None:
        for s in sources:
            if s["kind"] == "message":
                assert s["message_id"] in message_ids
            else:
                assert s["voice_note_id"] in voice_ids

    for term in data["terms"]:
        check(term["sources"])
        for alt in term["alternatives"]:
            check(alt["sources"])
    for flag in data["flags"]:
        check(flag["sources"])
    for recap in data["recaps"]:
        for line in recap["lines"]:
            check(line["sources"])
    for version in data["versions"]:
        for term in version["terms"]:
            check(term["sources"])
    for message in data["messages"]:
        assert message["sender_id"] in participant_ids
    for voice in data["voice_notes"]:
        assert voice["transcript_id"] in {t["id"] for t in data["transcripts"]}


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_score_points_add_up_to_the_total(path: Path) -> None:
    """Sanity check of the fixture only. The formula itself lives in packages/intelligence."""
    score = parsed(path)["score"][0]
    assert round(sum(item.points for item in score.breakdown)) == score.total


def test_the_ambiguous_score_follows_the_confirmed_term_rule() -> None:
    score = parsed(FIXTURES / "ambiguous.deal.json")["score"][0]
    by_key = {i.term_key: i for i in score.breakdown}
    assert by_key["delivery_date"].points == 0, (
        "an unclear term is never confirmed, so it earns nothing"
    )
    assert score.total == 55


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_only_confirmed_terms_are_in_versions(path: Path) -> None:
    for version in parsed(path)["versions"]:
        assert all(t.confirmed_at is not None for t in version.terms)


def test_the_fixtures_cover_the_main_cases() -> None:
    everything = {p.name: parsed(p) for p in DEALS}
    terms = [t for d in everything.values() for t in d["terms"]]
    assert {t.state for t in terms} == set(c.TermState)
    kinds = {t.value.kind for t in terms if t.value is not None}
    kinds |= {a.value.kind for t in terms for a in t.alternatives}
    for d in everything.values():
        for reveal in d["handshake_reveals"]:
            kinds |= {r.first.value.kind for r in reveal.rows} | {
                r.second.value.kind for r in reveal.rows
            }
    assert kinds == {k.value for k in c.ValueKind}
    flags = [f for d in everything.values() for f in d["flags"]]
    assert {f.kind for f in flags} >= {
        c.FlagKind.AMBIGUOUS, c.FlagKind.MISSING, c.FlagKind.CONTRADICTION, c.FlagKind.NEEDS_REVIEW,
    }  # fmt: skip
    assert any(f.cross_modal for f in flags)
    verdicts = {v.verdict for d in everything.values() for v in d["verify_results"]}
    assert verdicts == set(c.Verdict)
    assert any(
        r.result is c.RevealResult.MISMATCH
        for d in everything.values()
        for h in d["handshake_reveals"]
        for r in h.rows
    )


def test_fixtures_name_the_playbook_terms_of_the_local_model() -> None:
    expected = {
        "buyer", "seller", "item", "quantity", "unit_price", "total_amount", "advance_amount",
        "delivery_date", "balance_payment_date", "late_penalty", "quality_spec",
    }  # fmt: skip
    for path in DEALS:
        assert {t.key for t in parsed(path)["terms"]} == expected


# ---- the hashes in the fixtures are real (D1, D2, D5, D6) ----


def clean() -> dict[str, list[Any]]:
    return parsed(FIXTURES / "clean.deal.json")


def test_the_recap_hash_and_echo_code_do_not_depend_on_the_code() -> None:
    """D1: hash the content without the code, derive the code, then attach it."""
    recap = clean()["recaps"][0]
    content = {
        "deal_id": recap.deal_id,
        "version_n": recap.version_n,
        "language": recap.language.value,
        "lines": [dump(line) for line in recap.lines],
        "body_text": recap.body_text,
    }
    digest = recap_hash(content)
    assert to_hex(digest) == recap.recap_hash == recap.echo_code.recap_hash
    assert derive_echo_code(digest) == recap.echo_code.code
    assert (
        recap.text == recap.body_text + "\nIf all correct, reply: CONFIRM " + recap.echo_code.code
    )


def test_the_confirmation_reply_carries_the_echo_code() -> None:
    data = clean()
    code = data["recaps"][0].echo_code.code
    reply = [x for x in data["confirmations"] if x.reply_text][0]
    assert reply.code == code and code in reply.reply_text


def test_the_receipt_hash_covers_the_body_only() -> None:
    """D2: the hash sits outside the body and is not an input to itself."""
    receipt = clean()["receipts"][0]
    assert to_hex(receipt_hash(dump(receipt.body))) == receipt.receipt_hash
    assert receipt.receipt_hash not in json.dumps(dump(receipt.body))


@pytest.mark.parametrize("name", ["clean", "contradictory"])
def test_versions_keep_their_terms_sorted_by_key_and_the_digest_covers_the_snapshot(
    name: str,
) -> None:
    data = parsed(FIXTURES / f"{name}.deal.json")
    pairs = []
    for v in data["versions"]:
        digest = terms_digest(terms_set(v))
        assert to_hex(digest) == v.terms_digest
        pairs.append((digest, from_hex(v.root)))
    links = chain_links(pairs)
    assert [to_hex(x) for x in links] == [v.link for v in data["versions"]]
    chain = data["receipts"][0].body.chain
    assert [(x.version_n, x.link) for x in chain] == [
        (v.version_n, v.link) for v in data["versions"]
    ]


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_message_leaves_and_root_are_the_integrity_primitives(path: Path) -> None:
    data = parsed(path)
    rows = data["leaf_rows"]
    leaves = []
    for row, message in zip(rows, data["messages"], strict=True):
        record = dump(message)
        leaf = record_leaf(PREFIXES["MESSAGE"], bytes.fromhex(row.salt), record)
        assert to_hex(leaf) == row.leaf_hash
        assert to_hex(sha256(canonical_record(record))) == row.payload_digest
        assert row.payload == canonical_record(record).decode()
        leaves.append(leaf)
    body = data["receipts"][0].body
    assert body.leaf_count == len(rows)
    assert to_hex(merkle_root(leaves)) == body.root


def test_transcript_times_are_integer_milliseconds() -> None:
    transcript = parsed(FIXTURES / "contradictory.deal.json")["transcripts"][0]
    assert [(s.start_ms, s.end_ms) for s in transcript.spans] == [(0, 11500), (12000, 18000)]


def test_the_unions_round_trip() -> None:
    adapter = TypeAdapter(c.TermValue)
    for term in parsed(FIXTURES / "contradictory.deal.json")["terms"]:
        for alt in term.alternatives:
            assert adapter.validate_json(adapter.dump_json(alt.value)) == alt.value


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_version_terms_are_sorted_by_key(path: Path) -> None:
    for version in parsed(path)["versions"]:
        keys = [t.key for t in version.terms]
        assert keys == sorted(keys)
