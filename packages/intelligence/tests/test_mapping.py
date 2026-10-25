"""Mapping from the model's JSON to contract Terms (issues #63 and #64, Q-64)."""

import json
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from packages.contracts import (
    Confidence,
    EventValue,
    MessageSourceRef,
    MoneyValue,
    PartialDateValue,
    QuantityValue,
    Term,
    TermOrigin,
    TermState,
    TextValue,
    VoiceSourceRef,
)
from packages.intelligence.model_adapter import (
    ChatContext,
    ModelOutput,
    map_output,
    parse_model_output,
)
from packages.intelligence.tests.chat_builders import ChatBuilder


def output_of(terms: dict[str, Any]) -> ModelOutput:
    return parse_model_output(json.dumps({"deal_type": "supply_order", "terms": terms}))


def one(chat: ChatContext, key: str, term: dict[str, Any]) -> Term:
    terms = map_output(output_of({key: term}), chat)
    assert len(terms) == 1 and terms[0].key == key
    return terms[0]


@pytest.fixture
def ctx(mixed_chat: ChatBuilder) -> ChatContext:
    return mixed_chat.context()


def stated(value: Any, quote: str, msg: int) -> dict[str, Any]:
    return {"status": "stated", "value": value, "quote": [quote], "msg": [msg]}


# ---- dates (note 1) ----


def test_mm_dd_becomes_a_partial_date_with_leading_dashes(ctx: ChatContext) -> None:
    term = one(ctx, "delivery_date", stated("11-15", "15 November", 6))
    assert term.value == PartialDateValue(kind="partial_date", month_day="--11-15")
    assert term.state is TermState.STATED and not term.needs_review


def test_a_leap_day_is_accepted_without_a_year(ctx: ChatContext) -> None:
    term = one(ctx, "deadline", stated("02-29", "x", 6))
    assert term.value == PartialDateValue(kind="partial_date", month_day="--02-29")


@pytest.mark.parametrize("event", ["on_delivery", "on_completion"])
def test_event_names_become_event_values(ctx: ChatContext, event: str) -> None:
    term = one(ctx, "payment_date", stated(event, "on delivery", 6))
    assert term.value == EventValue(kind="event", event=event)


@pytest.mark.parametrize(
    "value", ["13-40", "00-10", "04-31", "1-5", "11/15", "2026-11-15", "soon", 1115, 11.15, ""]
)
def test_an_impossible_or_unknown_date_needs_review(ctx: ChatContext, value: Any) -> None:
    term = one(ctx, "delivery_date", stated(value, "15 November", 6))
    assert term.value is None and term.needs_review and term.confirmed_at is None
    assert term.raw is not None and "15 November" in term.raw
    assert term.confidence is Confidence.LOW


# ---- malformed output never raises (note 2) ----


@pytest.mark.parametrize(
    "term",
    [
        stated(480.5, "480", 1),
        {"status": "stated", "quote": ["480 each"], "msg": [1]},
        stated("480", "480", 1),
        stated(-5, "480", 1),
        stated(True, "480", 1),
        {"status": "maybe", "value": 480, "quote": ["480 each"], "msg": [1]},
        {"status": "stated", "value": 480, "quote": "480 each", "msg": [1]},
        "stated",
        None,
        {"status": "stated", "value": 480, "extra": 1},
    ],
)
def test_malformed_money_term_becomes_needs_review_not_an_exception(
    ctx: ChatContext, term: Any
) -> None:
    result = one(ctx, "unit_price", term)
    assert result.needs_review and result.value is None
    assert result.state is TermState.UNCLEAR and result.confidence is Confidence.LOW
    assert result.origin is TermOrigin.AI and result.confirmed_at is None
    assert result.raw  # the original text is kept
    Term.model_validate_json(result.model_dump_json())


def test_status_outside_the_four_keeps_the_quote_as_raw(ctx: ChatContext) -> None:
    result = one(
        ctx, "unit_price", {"status": "maybe", "value": 480, "quote": ["480 each ok?"], "msg": [1]}
    )
    assert result.raw == "480 each ok?" and result.needs_review
    assert [type(s) for s in result.sources] == [MessageSourceRef]


def test_one_bad_term_does_not_stop_the_others(ctx: ChatContext) -> None:
    output = output_of({"unit_price": "junk", "buyer": stated("Raju", "Raju", 1)})
    terms = {t.key: t for t in map_output(output, ctx)}
    assert terms["unit_price"].needs_review
    assert (
        terms["buyer"].value == TextValue(kind="text", text="Raju")
        and not terms["buyer"].needs_review
    )


JSON_VALUES = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(max_size=8),
    lambda inner: (
        st.lists(inner, max_size=3) | st.dictionaries(st.text(max_size=6), inner, max_size=4)
    ),
    max_leaves=8,
)


@settings(max_examples=150, deadline=None)
@given(
    st.dictionaries(
        st.sampled_from(["unit_price", "quantity", "delivery_date", "buyer", "other"]),
        st.one_of(
            JSON_VALUES,
            st.fixed_dictionaries(
                {"status": st.sampled_from(["stated", "unclear", "contradicted", "missing", "x"])},
                optional={
                    "value": JSON_VALUES,
                    "quote": JSON_VALUES,
                    "msg": JSON_VALUES,
                    "reason": JSON_VALUES,
                },
            ),
        ),
        max_size=5,
    )
)
def test_no_model_output_can_make_the_mapping_raise(terms: dict[str, Any]) -> None:
    chat = ChatBuilder()
    chat.say("Raju", "200 shirts, 480 each ok?")
    chat.say("Meena", "ok")
    mapped = map_output(output_of(terms), chat.context())
    for term in mapped:
        assert term.confirmed_at is None and term.origin is TermOrigin.AI


# ---- message numbers (note 3) ----


def test_positions_count_media_deleted_voice_and_system_lines(
    ctx: ChatContext, mixed_chat: ChatBuilder
) -> None:
    term = one(ctx, "advance_amount", stated(48000, "advance 48000 received", 6))
    (source,) = term.sources
    assert isinstance(source, MessageSourceRef)
    assert source.message_id == mixed_chat.messages[5].id
    assert source.quote == "advance 48000 received"
    first = one(ctx, "quantity", stated(200, "200 shirts", 1))
    assert isinstance(first.sources[0], MessageSourceRef)
    assert first.sources[0].message_id == mixed_chat.messages[0].id


def test_a_quote_in_a_system_or_media_line_maps_to_that_line(
    ctx: ChatContext, mixed_chat: ChatBuilder
) -> None:
    term = one(
        ctx,
        "scope",
        {
            "status": "unclear",
            "value": None,
            "quote": ["<Media omitted>"],
            "msg": [3],
            "reason": "vague_spec",
        },
    )
    assert isinstance(term.sources[0], MessageSourceRef)
    assert term.sources[0].message_id == mixed_chat.messages[2].id


@pytest.mark.parametrize("msg", [0, 7, 99, -1])
def test_a_position_outside_the_chat_drops_the_source_and_needs_review(
    ctx: ChatContext, msg: int
) -> None:
    term = one(ctx, "quantity", stated(200, "200 shirts", msg))
    assert term.sources == [] and term.needs_review


def test_quote_and_msg_lists_of_different_length_need_review(ctx: ChatContext) -> None:
    term = one(
        ctx, "item", {"status": "stated", "value": "shirts", "quote": ["shirts"], "msg": [1, 6]}
    )
    assert term.needs_review
    assert len(term.sources) == 2


def test_repeated_source_is_listed_once(ctx: ChatContext) -> None:
    term = one(
        ctx,
        "item",
        {"status": "stated", "value": "shirts", "quote": ["shirts", "shirts"], "msg": [1, 1]},
    )
    assert len(term.sources) == 1 and not term.needs_review


# ---- voice sources (note 4) ----


def test_a_quote_inside_one_span_gets_that_spans_times(
    ctx: ChatContext, mixed_chat: ChatBuilder
) -> None:
    term = one(ctx, "advance_amount", stated(4800000 // 100, "forty eight thousand", 5))
    (source,) = term.sources
    assert isinstance(source, VoiceSourceRef)
    assert (source.start_ms, source.end_ms) == (2400, 5100)
    assert source.voice_note_id == mixed_chat.voice[mixed_chat.messages[4].id].voice_note_id
    assert source.quote == "forty eight thousand" and not term.needs_review


def test_a_quote_across_two_spans_covers_both(ctx: ChatContext) -> None:
    term = one(ctx, "advance_amount", stated(48000, "send the advance forty eight thousand", 5))
    (source,) = term.sources
    assert isinstance(source, VoiceSourceRef)
    assert (source.start_ms, source.end_ms) == (0, 5100)


def test_a_quote_in_the_first_span(ctx: ChatContext) -> None:
    term = one(ctx, "item", stated("advance", "I will send", 5))
    (source,) = term.sources
    assert isinstance(source, VoiceSourceRef) and (source.start_ms, source.end_ms) == (0, 2400)


def test_a_quote_not_in_the_transcript_keeps_a_message_source_and_needs_review(
    ctx: ChatContext, mixed_chat: ChatBuilder
) -> None:
    term = one(ctx, "advance_amount", stated(48000, "fifty thousand", 5))
    (source,) = term.sources
    assert isinstance(source, MessageSourceRef)
    assert source.message_id == mixed_chat.messages[4].id and source.quote is None
    assert term.needs_review


def test_a_voice_message_without_a_transcript_is_a_message_source(chat: ChatBuilder) -> None:
    chat.say("Meena", "<attached: voice.opus>", attachment="c" * 64)
    term = one(chat.context(), "item", stated("x", "<attached: voice.opus>", 1))
    assert isinstance(term.sources[0], MessageSourceRef) and not term.needs_review


# ---- integers and money (notes 5 and 6) ----


@pytest.mark.parametrize("key", ["quantity", "revisions"])
def test_integers_become_quantities_without_a_unit(ctx: ChatContext, key: str) -> None:
    term = one(ctx, key, stated(200, "200 shirts", 1))
    assert term.value == QuantityValue(kind="quantity", amount="200", unit=None)


def test_zero_is_a_valid_quantity(ctx: ChatContext) -> None:
    assert one(ctx, "revisions", stated(0, "no revisions", 6)).value == QuantityValue(
        kind="quantity", amount="0", unit=None
    )


@pytest.mark.parametrize(
    ("rupees", "paise"),
    [(480, "48000"), (48000, "4800000"), (0, "0"), (1, "100"), (10**15, str(10**17))],
)
def test_rupees_become_paise_text(ctx: ChatContext, rupees: int, paise: str) -> None:
    quote = f"{rupees}"
    chat = ChatBuilder()
    chat.say("Raju", f"pay {quote}")
    term = one(chat.context(), "fee", stated(rupees, quote, 1))
    assert term.value == MoneyValue(kind="money", paise=paise)


# ---- statuses ----


def test_missing_has_no_value_and_no_sources(ctx: ChatContext) -> None:
    term = one(ctx, "total_amount", {"status": "missing"})
    assert term.state is TermState.MISSING and term.value is None and term.sources == []
    assert not term.needs_review


def test_unclear_keeps_its_reason_and_quote(ctx: ChatContext) -> None:
    term = one(
        ctx,
        "delivery_date",
        {
            "status": "unclear",
            "value": None,
            "quote": ["delivery on 15 November"],
            "msg": [6],
            "reason": "relative_date",
        },
    )
    assert term.state is TermState.UNCLEAR and term.unclear_reason == "relative_date"
    assert term.value is None and not term.needs_review and len(term.sources) == 1


def test_an_unknown_unclear_reason_needs_review(ctx: ChatContext) -> None:
    term = one(
        ctx,
        "delivery_date",
        {
            "status": "unclear",
            "value": None,
            "quote": ["delivery"],
            "msg": [6],
            "reason": "because",
        },
    )
    assert term.needs_review and term.unclear_reason == "because"


def test_every_known_reason_is_accepted(ctx: ChatContext) -> None:
    for reason in [
        "relative_date",
        "approximate_amount",
        "vague_timing",
        "conditional",
        "unspecified_unit",
        "unconfirmed",
        "vague_spec",
    ]:
        term = one(
            ctx,
            "scope",
            {
                "status": "unclear",
                "value": None,
                "quote": ["delivery"],
                "msg": [6],
                "reason": reason,
            },
        )
        assert not term.needs_review, reason


def test_contradicted_keeps_both_sources_and_no_value(ctx: ChatContext) -> None:
    term = one(
        ctx,
        "total_amount",
        {
            "status": "contradicted",
            "value": None,
            "quote": ["200 shirts", "advance 48000 received"],
            "msg": [1, 6],
        },
    )
    assert term.state is TermState.CONTRADICTED and term.value is None
    assert len(term.sources) == 2


def test_a_stated_term_without_any_source_needs_review(ctx: ChatContext) -> None:
    term = one(ctx, "buyer", {"status": "stated", "value": "Raju"})
    assert term.needs_review and term.sources == []


# ---- grounding and the rules safety net ----


def test_a_quote_that_is_not_in_its_message_is_not_grounded(ctx: ChatContext) -> None:
    term = one(ctx, "quantity", stated(200, "two hundred shirts", 1))
    assert term.needs_review and term.confidence is Confidence.LOW
    assert isinstance(term.sources[0], MessageSourceRef) and term.sources[0].quote is None


def test_a_grounded_quote_that_agrees_is_medium_confidence(ctx: ChatContext) -> None:
    term = one(ctx, "quantity", stated(200, "200 shirts", 1))
    assert term.confidence is Confidence.MEDIUM and not term.needs_review


def test_value_that_disagrees_with_its_own_quote_is_flagged_and_kept(ctx: ChatContext) -> None:
    term = one(ctx, "unit_price", stated(48000, "480 each ok?", 1))
    assert term.needs_review and term.confidence is Confidence.LOW
    assert term.value == MoneyValue(kind="money", paise="4800000")  # the value is never changed


@pytest.mark.parametrize("quote", ["480 each ok?", "Rs 480", "₹480/-"])
def test_value_that_agrees_with_its_quote_passes(quote: str) -> None:
    chat = ChatBuilder()
    chat.say("Raju", quote)
    assert not one(chat.context(), "unit_price", stated(480, quote, 1)).needs_review


def test_indian_digit_grouping_in_a_quote_is_read(ctx: ChatContext) -> None:
    chat = ChatBuilder()
    chat.say("Raju", "total ₹4,80,000 only")
    assert not one(
        chat.context(), "total_amount", stated(480000, "total ₹4,80,000 only", 1)
    ).needs_review


def test_quantity_that_disagrees_with_its_quote_is_flagged(ctx: ChatContext) -> None:
    assert one(ctx, "quantity", stated(20, "200 shirts", 1)).needs_review


def test_unclear_term_whose_quote_holds_a_clear_amount_is_flagged() -> None:
    chat = ChatBuilder()
    chat.say("Raju", "sent 15600 rs advance")
    term = one(
        chat.context(),
        "advance_amount",
        {
            "status": "unclear",
            "value": None,
            "quote": ["sent 15600 rs advance"],
            "msg": [1],
            "reason": "unconfirmed",
        },
    )
    assert term.needs_review


def test_unclear_term_without_an_amount_is_not_flagged() -> None:
    chat = ChatBuilder()
    chat.say("Raju", "advance half now")
    term = one(
        chat.context(),
        "advance_amount",
        {
            "status": "unclear",
            "value": None,
            "quote": ["advance half now"],
            "msg": [1],
            "reason": "unspecified_unit",
        },
    )
    assert not term.needs_review


@pytest.mark.parametrize("key", ["item", "scope", "late_penalty"])
def test_a_sender_name_is_not_grounding_for_a_non_party_term(ctx: ChatContext, key: str) -> None:
    term = one(ctx, key, stated("x", "Raju", 1))
    assert term.needs_review and term.confidence is Confidence.LOW
    assert isinstance(term.sources[0], MessageSourceRef) and term.sources[0].quote is None


@pytest.mark.parametrize("key", ["buyer", "seller", "client", "freelancer"])
def test_a_sender_name_grounds_a_party_term(ctx: ChatContext, key: str) -> None:
    assert not one(ctx, key, stated("Raju", "Raju", 1)).needs_review


def test_a_party_quote_must_be_the_sender_of_that_message(ctx: ChatContext) -> None:
    assert one(ctx, "buyer", stated("Meena", "Meena", 1)).needs_review  # message 1 is Raju's


# ---- the AI never confirms, ids are stable ----


def test_terms_are_never_confirmed_and_always_ai(ctx: ChatContext) -> None:
    output = output_of({"buyer": stated("Raju", "Raju", 1), "total_amount": {"status": "missing"}})
    for term in map_output(output, ctx):
        assert term.origin is TermOrigin.AI
        assert term.confirmed_at is None and term.confirmed_by is None
        assert term.acknowledged_by_other is False and term.deal_id == ctx.deal_id


def test_ids_are_deterministic_and_differ_by_key(ctx: ChatContext) -> None:
    output = output_of({"buyer": stated("Raju", "Raju", 1), "seller": stated("Meena", "Meena", 2)})
    first, second = map_output(output, ctx), map_output(output, ctx)
    assert [t.id for t in first] == [t.id for t in second]
    assert len({t.id for t in first}) == 2


def test_text_values_become_text(ctx: ChatContext) -> None:
    assert one(ctx, "buyer", stated("Raju", "Raju", 1)).value == TextValue(kind="text", text="Raju")
    assert one(ctx, "buyer", stated("", "Raju", 1)).needs_review


# ---- the recorded real output ----


def test_the_recorded_real_mistake_is_caught_by_the_safety_net() -> None:
    chat = ChatBuilder()
    chat.say("Raju", "200 shirts, 480 each ok?")
    chat.say("Meena", "ok. delivery next week")
    chat.say("Raju", "advance half now")
    chat.say("Meena", "done sent 48000")
    from pathlib import Path

    recorded = json.loads(
        (
            Path(__file__).resolve().parents[1] / "fixtures" / "recordings" / "raju-meena-v1.json"
        ).read_text(encoding="utf-8")
    )
    terms = {
        t.key: t for t in map_output(ModelOutput.model_validate(recorded["output"]), chat.context())
    }
    assert terms["unit_price"].needs_review  # value 48000 against the quote "480 each ok?"
    assert terms["quantity"].value == QuantityValue(kind="quantity", amount="200", unit=None)
    assert terms["delivery_date"].state is TermState.UNCLEAR
    assert terms["delivery_date"].unclear_reason == "relative_date"
    assert terms["advance_amount"].state is TermState.UNCLEAR  # the advance in message 4 is missed
    assert terms["total_amount"].state is TermState.MISSING
    assert not terms["buyer"].needs_review
