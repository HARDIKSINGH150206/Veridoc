"""Demo recap with an echo code for the walking skeleton (issue #29)."""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from packages.contracts import (
    AgreedTerm,
    DateValue,
    EventValue,
    Language,
    MessageSourceRef,
    MoneyValue,
    QuantityValue,
    Recap,
    TextValue,
)
from packages.ingest.demo_recap import ConfirmationRequired, build_demo_recap
from packages.integrity import JsonValue, derive_echo_code, recap_hash, to_hex

NS = uuid.UUID("2f2c7a0e-6a41-4bb0-9a43-0b1f7a3b9d10")
DEAL = str(uuid.uuid5(NS, "deal"))
OTHER_DEAL = str(uuid.uuid5(NS, "other deal"))
ME = str(uuid.uuid5(NS, "me"))
MESSAGE = str(uuid.uuid5(NS, "message"))
NOW = datetime(2026, 10, 25, 11, 0, 0, tzinfo=timezone(timedelta(minutes=330)))


def agreed(key: str, value: Any, quote: str = "x") -> AgreedTerm:
    return AgreedTerm(
        key=key,
        value=value,
        sources=(MessageSourceRef(kind="message", message_id=MESSAGE, quote=quote),),
        confirmed_by=ME,
        confirmed_at=NOW,
    )


def terms() -> list[AgreedTerm]:
    return [
        agreed("unit_price", MoneyValue(kind="money", paise="48000")),
        agreed("quantity", QuantityValue(kind="quantity", amount="200", unit="shirts")),
        agreed("delivery_date", DateValue(kind="date", date="2026-11-15")),
        agreed("balance_payment_date", EventValue(kind="event", event="on_delivery")),
        agreed("buyer", TextValue(kind="text", text="Bilal")),
    ]


def build(items: list[AgreedTerm] | None = None, *, deal: str = DEAL, version: int = 1) -> Recap:
    return build_demo_recap(deal, version, items if items is not None else terms(), NOW)


def test_recap_is_a_valid_contract_recap_with_lines_in_key_order() -> None:
    recap = build()
    Recap.model_validate_json(recap.model_dump_json())
    assert [line.term_key for line in recap.lines] == sorted(t.key for t in terms())
    assert recap.language is Language.EN and recap.deal_id == DEAL and recap.version_n == 1
    assert recap.created_at == NOW


def test_each_line_links_to_its_terms_sources() -> None:
    by_key = {t.key: t for t in terms()}
    for line in build().lines:
        assert line.sources == by_key[line.term_key].sources
        assert line.text


def test_lines_state_the_confirmed_values() -> None:
    text = {line.term_key: line.text for line in build().lines}
    assert "480" in text["unit_price"]
    assert "200" in text["quantity"] and "shirts" in text["quantity"]
    assert "2026-11-15" in text["delivery_date"]
    assert "on delivery" in text["balance_payment_date"]
    assert "Bilal" in text["buyer"]


def test_the_hash_and_echo_code_follow_the_spec_recipe() -> None:
    """INTEGRITY_SPEC section 7: hash the content without the code, derive the code from it."""
    recap = build()
    content: dict[str, JsonValue] = {
        "deal_id": recap.deal_id,
        "version_n": recap.version_n,
        "language": recap.language.value,
        "lines": [line.model_dump(mode="json") for line in recap.lines],
        "body_text": recap.body_text,
    }
    digest = recap_hash(content)
    assert recap.recap_hash == to_hex(digest) == recap.echo_code.recap_hash
    assert recap.echo_code.code == derive_echo_code(digest)
    assert recap.echo_code.version_n == recap.version_n


def test_the_sent_text_is_the_body_plus_the_code_line_and_the_body_has_no_code() -> None:
    recap = build()
    assert recap.text == f"{recap.body_text}\nIf all correct, reply: CONFIRM {recap.echo_code.code}"
    assert "CONFIRM" not in recap.body_text


def test_a_code_cannot_be_reused_across_versions_or_deals() -> None:
    base = build()
    next_version = build(version=2)
    other_deal = build(deal=OTHER_DEAL)
    assert len({base.recap_hash, next_version.recap_hash, other_deal.recap_hash}) == 3
    assert base.echo_code.recap_hash != next_version.echo_code.recap_hash


def test_changing_a_term_changes_the_recap_hash() -> None:
    items = terms()
    items[0] = agreed("unit_price", MoneyValue(kind="money", paise="48100"))
    assert build(items).recap_hash != build().recap_hash


def test_the_same_input_gives_the_same_recap() -> None:
    assert build() == build()
    assert build().id == build().id


def test_no_confirmed_terms_means_no_recap() -> None:
    with pytest.raises(ConfirmationRequired):
        build([])


def test_the_recap_hash_does_not_depend_on_the_clock() -> None:
    later = build_demo_recap(DEAL, 1, terms(), NOW + timedelta(hours=1))
    assert later.recap_hash == build().recap_hash and json.loads(later.model_dump_json())


# ---- checking confirmed terms against a sample ----


def test_confirmed_terms_must_come_from_the_primary_user_and_the_samples_messages() -> None:
    from pathlib import Path

    from packages.ingest.demo_recap import InvalidConfirmation, check_confirmed_terms
    from packages.ingest.samples import load_sample

    sample = load_sample("clean", Path(__file__).resolve().parents[1] / "fixtures")
    me = next(p.id for p in sample.participants if p.is_me)
    other = next(p.id for p in sample.participants if not p.is_me)
    message = sample.messages[0].id

    def term(by: str, source: str) -> AgreedTerm:
        return AgreedTerm(
            key="buyer",
            value=TextValue(kind="text", text="x"),
            sources=(MessageSourceRef(kind="message", message_id=source, quote=None),),
            confirmed_by=by,
            confirmed_at=NOW,
        )

    check_confirmed_terms(sample, [term(me, message)])
    with pytest.raises(InvalidConfirmation):
        check_confirmed_terms(sample, [term(other, message)])
    with pytest.raises(InvalidConfirmation):
        check_confirmed_terms(sample, [term(me, MESSAGE)])
    with pytest.raises(ConfirmationRequired):
        check_confirmed_terms(sample, [])
    with pytest.raises(InvalidConfirmation):
        check_confirmed_terms(sample, [term(me, message), term(me, message)])  # duplicate key
