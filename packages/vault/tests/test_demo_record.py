"""Demo record for the walking skeleton (issue #31): real hashes over demo data."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from packages.contracts import (
    AgreedTerm,
    MessageSourceRef,
    MoneyValue,
    PlaybookRef,
    Receipt,
    TextValue,
)
from packages.ingest.samples import Sample, load_sample
from packages.integrity import (
    PREFIXES,
    canonical_record,
    chain_links,
    leaf_hash,
    merkle_root,
    payload_digest,
    receipt_hash,
    terms_digest,
    to_hex,
)
from packages.vault.demo_record import DEMO_SPEC_VERSION, DemoRecordError, record_demo

FIXTURES = Path(__file__).resolve().parents[2] / "ingest" / "fixtures"
NOW = datetime(2026, 10, 25, 11, 0, 0, tzinfo=timezone(timedelta(minutes=330)))
PLAYBOOK = PlaybookRef(key="supply_order", version=1)


@pytest.fixture
def sample() -> Sample:
    return load_sample("clean", FIXTURES)


def salts(count: int) -> list[bytes]:
    return [bytes([i + 1]) * 16 for i in range(count)]


def agreed(sample: Sample, key: str, value: Any) -> AgreedTerm:
    me = next(p.id for p in sample.participants if p.is_me)
    return AgreedTerm(
        key=key,
        value=value,
        sources=(MessageSourceRef(kind="message", message_id=sample.messages[0].id, quote=None),),
        confirmed_by=me,
        confirmed_at=NOW,
    )


def terms(sample: Sample) -> list[AgreedTerm]:
    return [
        agreed(sample, "unit_price", MoneyValue(kind="money", paise="48000")),
        agreed(sample, "buyer", TextValue(kind="text", text="Bilal")),
    ]


def build(sample: Sample, items: list[AgreedTerm] | None = None) -> Any:
    return record_demo(
        list(sample.messages),
        items if items is not None else terms(sample),
        PLAYBOOK,
        salts(len(sample.messages)),
        NOW,
    )


def test_the_receipt_is_a_valid_envelope_labelled_as_a_demo(sample: Sample) -> None:
    record = build(sample)
    Receipt.model_validate_json(record.receipt.model_dump_json())
    body = record.receipt.body
    assert body.spec_version == DEMO_SPEC_VERSION and "demo" in DEMO_SPEC_VERSION
    assert body.deal_id == sample.messages[0].deal_id and body.anchor is None
    assert body.recorded_at == NOW and body.leaf_count == len(sample.messages)


def test_every_hash_can_be_recomputed_from_the_leaf_rows(sample: Sample) -> None:
    """The verification steps of INTEGRITY_SPEC section 10, written independently of the builder."""
    record = build(sample)
    leaves = []
    for row in record.leaf_rows:
        assert row.payload is not None and row.salt is not None
        digest = payload_digest(row.payload.encode("utf-8"))
        assert to_hex(digest) == row.payload_digest
        leaf = leaf_hash(PREFIXES["MESSAGE"], bytes.fromhex(row.salt), digest)
        assert to_hex(leaf) == row.leaf_hash
        leaves.append(leaf)
    assert [r.seq for r in record.leaf_rows] == list(range(1, len(leaves) + 1))
    root = merkle_root(leaves)
    body = record.receipt.body
    assert to_hex(root) == body.root

    version = record.version
    terms_set = {
        "deal_id": version.deal_id,
        "version_n": 1,
        "playbook": PLAYBOOK.model_dump(mode="json"),
        "terms": [t.model_dump(mode="json") for t in sorted(version.terms, key=lambda t: t.key)],
    }
    digest = terms_digest(terms_set)
    (link,) = chain_links([(digest, root)])
    (entry,) = body.chain
    assert (entry.version_n, entry.terms_digest, entry.root, entry.link) == (
        1, to_hex(digest), to_hex(root), to_hex(link),
    )  # fmt: skip
    assert (version.terms_digest, version.root, version.link) == (
        to_hex(digest), to_hex(root), to_hex(link),
    )  # fmt: skip
    assert version.prev_link is None and version.reason_message_id is None

    assert record.receipt.receipt_hash == to_hex(receipt_hash(body.model_dump(mode="json")))
    assert record.receipt.receipt_hash not in json.dumps(body.model_dump(mode="json"))


def test_leaf_payloads_are_the_canonical_messages(sample: Sample) -> None:
    record = build(sample)
    for row, message in zip(record.leaf_rows, sample.messages, strict=True):
        assert row.payload == canonical_record(message.model_dump(mode="json")).decode()
        assert row.leaf_type.value == "message"


def test_version_terms_are_sorted_by_key(sample: Sample) -> None:
    assert [t.key for t in build(sample).version.terms] == ["buyer", "unit_price"]


def test_changing_a_message_or_a_term_changes_the_root_and_the_chain(sample: Sample) -> None:
    base = build(sample)
    edited = sample.messages[0].model_copy(update={"text": "different words"})
    messages = [edited, *sample.messages[1:]]
    changed = record_demo(messages, terms(sample), PLAYBOOK, salts(len(messages)), NOW)
    assert changed.receipt.body.root != base.receipt.body.root
    other_terms = terms(sample)
    other_terms[0] = agreed(sample, "unit_price", MoneyValue(kind="money", paise="48100"))
    again = build(sample, other_terms)
    assert again.receipt.body.root == base.receipt.body.root  # terms are not leaves here
    assert again.version.terms_digest != base.version.terms_digest
    assert again.receipt.body.chain[0].link != base.receipt.body.chain[0].link
    assert again.receipt.receipt_hash != base.receipt.receipt_hash


def test_same_inputs_give_the_same_record(sample: Sample) -> None:
    assert build(sample) == build(sample)


def test_different_salts_hide_the_same_messages_behind_different_leaves(sample: Sample) -> None:
    other = record_demo(
        list(sample.messages),
        terms(sample),
        PLAYBOOK,
        [bytes([0xA0 + i]) * 16 for i in range(len(sample.messages))],
        NOW,
    )
    assert other.receipt.body.root != build(sample).receipt.body.root


def test_bad_input_is_rejected(sample: Sample) -> None:
    with pytest.raises(DemoRecordError):
        record_demo([], terms(sample), PLAYBOOK, [], NOW)
    with pytest.raises(DemoRecordError):
        record_demo(list(sample.messages), [], PLAYBOOK, salts(len(sample.messages)), NOW)
    with pytest.raises(DemoRecordError):
        record_demo(list(sample.messages), terms(sample), PLAYBOOK, salts(2), NOW)
    with pytest.raises(DemoRecordError):
        record_demo(
            list(sample.messages), terms(sample), PLAYBOOK, [b"short"] * len(sample.messages), NOW
        )
    mixed = [sample.messages[0].model_copy(update={"deal_id": sample.messages[1].id})]
    mixed += list(sample.messages[1:])
    with pytest.raises(DemoRecordError):
        record_demo(mixed, terms(sample), PLAYBOOK, salts(len(mixed)), NOW)
    with pytest.raises(DemoRecordError):
        record_demo(
            list(reversed(sample.messages)),
            terms(sample),
            PLAYBOOK,
            salts(len(sample.messages)),
            NOW,
        )
