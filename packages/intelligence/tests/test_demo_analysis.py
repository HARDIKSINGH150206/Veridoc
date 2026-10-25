"""Demo analysis for the walking skeleton (issue #30): recorded model output to Terms."""

from pathlib import Path

import pytest

from packages.contracts import (
    MessageSourceRef,
    MoneyValue,
    PartialDateValue,
    QuantityValue,
    Term,
    TermOrigin,
    TermState,
    TextValue,
)
from packages.ingest.samples import Sample, load_sample
from packages.intelligence.demo_analysis import analyze_demo, chat_context
from packages.intelligence.model_adapter import (
    FakeModelAdapter,
    UnrecordedChat,
    load_recordings,
    numbered_chat,
)

INGEST = Path(__file__).resolve().parents[2] / "ingest" / "fixtures"
RECORDINGS = Path(__file__).resolve().parents[1] / "fixtures" / "recordings"
SAMPLES = ("clean", "ambiguous", "contradictory")
MODEL_KEYS = {
    "buyer", "seller", "item", "quantity", "unit_price", "total_amount", "advance_amount",
    "delivery_date", "balance_payment_date", "late_penalty", "quality_spec",
}  # fmt: skip


def analyze(name: str) -> tuple[Sample, dict[str, Term]]:
    sample = load_sample(name, INGEST)
    adapter = FakeModelAdapter(load_recordings(RECORDINGS))
    return sample, {t.key: t for t in analyze_demo(sample, adapter)}


@pytest.mark.parametrize("name", SAMPLES)
def test_every_sample_has_a_recording_for_its_exact_numbered_chat(name: str) -> None:
    sample = load_sample(name, INGEST)
    chats = {r.numbered_chat for r in load_recordings(RECORDINGS)}
    assert numbered_chat(chat_context(sample)) in chats


@pytest.mark.parametrize("name", SAMPLES)
def test_terms_are_the_playbook_terms_proposed_by_the_ai_and_unconfirmed(name: str) -> None:
    _, terms = analyze(name)
    assert set(terms) == MODEL_KEYS
    for term in terms.values():
        assert term.origin is TermOrigin.AI
        assert term.confirmed_at is None and term.confirmed_by is None


@pytest.mark.parametrize("name", SAMPLES)
def test_every_source_links_to_a_real_message_and_a_grounded_quote(name: str) -> None:
    sample, terms = analyze(name)
    by_id = {m.id: m for m in sample.messages}
    for term in terms.values():
        assert (term.state is TermState.MISSING) == (not term.sources)
        for source in term.sources:
            assert isinstance(source, MessageSourceRef) and source.message_id in by_id
            if source.quote is not None:
                assert source.quote in by_id[source.message_id].text


def test_clean_sample_values() -> None:
    _, terms = analyze("clean")
    assert terms["unit_price"].value == MoneyValue(kind="money", paise="48000")
    assert terms["total_amount"].value == MoneyValue(kind="money", paise="9600000")
    assert terms["advance_amount"].value == MoneyValue(kind="money", paise="4800000")
    assert terms["quantity"].value == QuantityValue(kind="quantity", amount="200", unit=None)
    assert terms["delivery_date"].value == PartialDateValue(
        kind="partial_date", month_day="--11-15"
    )
    assert terms["buyer"].value == TextValue(kind="text", text="Bilal")
    assert terms["quality_spec"].state is TermState.MISSING
    assert not any(t.needs_review for t in terms.values()), "the clean recording passes every check"


def test_ambiguous_sample_leaves_delivery_unclear_and_the_rest_missing() -> None:
    _, terms = analyze("ambiguous")
    assert terms["delivery_date"].state is TermState.UNCLEAR
    assert terms["delivery_date"].unclear_reason == "relative_date"
    assert terms["balance_payment_date"].state is TermState.MISSING
    assert terms["late_penalty"].state is TermState.MISSING


def test_contradictory_sample_has_a_conflicting_total_with_two_sources() -> None:
    sample, terms = analyze("contradictory")
    total = terms["total_amount"]
    assert total.state is TermState.CONTRADICTED and total.value is None
    assert [s.message_id for s in total.sources if isinstance(s, MessageSourceRef)] == [
        sample.messages[0].id,
        sample.messages[1].id,
    ]


def test_a_chat_without_a_recording_raises_unrecorded_chat() -> None:
    sample = load_sample("clean", INGEST)
    edited = sample.messages[0].model_copy(update={"text": "something nobody recorded"})
    changed = Sample(sample.playbook_id, sample.participants, (edited, *sample.messages[1:]))
    with pytest.raises(UnrecordedChat):
        analyze_demo(changed, FakeModelAdapter(load_recordings(RECORDINGS)))
