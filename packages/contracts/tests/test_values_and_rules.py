"""Typed values and the structural rules (D1 to D7 and the 15 answers of PR #40)."""

import json
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import TypeAdapter, ValidationError

import packages.contracts as c

A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"
H = "a" * 64
IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime(2026, 10, 12, 10, 2, 0, tzinfo=IST)
VALUE = TypeAdapter(c.TermValue)


# ---- typed values (answer 2, money and large numbers as text) ----


def test_value_union_picks_the_model_by_kind() -> None:
    cases = {
        "money": {"kind": "money", "paise": "4800000"},
        "quantity": {"kind": "quantity", "amount": "200", "unit": "shirts"},
        "date": {"kind": "date", "date": "2026-11-15"},
        "partial_date": {"kind": "partial_date", "month_day": "--11-15"},
        "event": {"kind": "event", "event": "on_delivery"},
        "duration": {"kind": "duration", "amount": 30, "unit": "days"},
        "text": {"kind": "text", "text": "Raju"},
    }
    assert {k.value for k in c.ValueKind} == set(cases)
    for kind, data in cases.items():
        assert VALUE.validate_json(json.dumps(data)).kind == kind


@pytest.mark.parametrize("paise", ["-1", "01", "1.5", " 1", "", "1e3", "12 000"])
def test_money_is_a_plain_non_negative_whole_number_as_text(paise: str) -> None:
    with pytest.raises(ValidationError):
        c.MoneyValue(kind="money", paise=paise)


def test_money_is_text_so_huge_amounts_stay_exact() -> None:
    value = c.MoneyValue(kind="money", paise="99999999999999999999999")
    assert value.paise == "99999999999999999999999"
    with pytest.raises(ValidationError):
        c.MoneyValue(kind="money", paise=4800000)  # type: ignore[arg-type]


def test_dates_must_be_real_and_the_year_is_required_for_a_full_date() -> None:
    c.DateValue(kind="date", date="2028-02-29")
    for bad in ("2026-02-30", "2026-13-01", "26-11-15", "--11-15", "2026-1-5"):
        with pytest.raises(ValidationError):
            c.DateValue(kind="date", date=bad)


def test_partial_dates_have_no_year_and_must_be_real() -> None:
    c.PartialDateValue(kind="partial_date", month_day="--02-29")
    for bad in ("--13-01", "--02-30", "11-15", "2026-11-15", "--1-5"):
        with pytest.raises(ValidationError):
            c.PartialDateValue(kind="partial_date", month_day=bad)


@pytest.mark.parametrize("name", ["on_delivery", "on_completion", "x"])
def test_event_names(name: str) -> None:
    assert c.EventValue(kind="event", event=name).event == name


@pytest.mark.parametrize("name", ["On_Delivery", "1abc", "on delivery", ""])
def test_bad_event_names(name: str) -> None:
    with pytest.raises(ValidationError):
        c.EventValue(kind="event", event=name)


def test_durations_are_whole_calendar_units() -> None:
    days = c.DurationUnit.DAYS
    c.DurationValue(kind="duration", amount=30, unit=days)
    with pytest.raises(ValidationError):
        c.DurationValue(kind="duration", amount=-1, unit=days)
    with pytest.raises(ValidationError):
        c.DurationValue(kind="duration", amount=2**60, unit=days)
    with pytest.raises(ValidationError):
        c.DurationValue(kind="duration", amount=1, unit="hours")  # type: ignore[arg-type]


# ---- term states and rules (handover statuses, answer 4) ----


def term(**kw: object) -> c.Term:
    base: dict[str, object] = {
        "id": A, "deal_id": B, "key": "unit_price", "value": None, "raw": None,
        "state": c.TermState.MISSING, "unclear_reason": None, "origin": c.TermOrigin.RULES,
        "confidence": c.Confidence.HIGH, "needs_review": False, "sources": [], "alternatives": [],
        "confirmed_at": None, "confirmed_by": None, "acknowledged_by_other": False,
    }  # fmt: skip
    base.update(kw)
    return c.Term(**base)  # type: ignore[arg-type]


def test_term_states_are_exactly_the_four_model_statuses() -> None:
    assert [s.value for s in c.TermState] == ["stated", "unclear", "contradicted", "missing"]


def test_a_missing_term_is_valid_and_has_no_value_or_sources() -> None:
    assert term().state is c.TermState.MISSING
    with pytest.raises(ValidationError):
        term(sources=[c.MessageSourceRef(kind="message", message_id=A)])


def test_a_value_is_present_exactly_when_the_term_is_stated() -> None:
    money = c.MoneyValue(kind="money", paise="100")
    source = c.MessageSourceRef(kind="message", message_id=A)
    assert term(state=c.TermState.STATED, value=money, sources=[source]).value == money
    with pytest.raises(ValidationError):
        term(state=c.TermState.STATED, value=None, sources=[source])
    for state in (c.TermState.UNCLEAR, c.TermState.CONTRADICTED, c.TermState.MISSING):
        with pytest.raises(ValidationError):
            term(state=state, value=money)


def test_an_unclear_reason_only_goes_with_an_unclear_term() -> None:
    source = c.MessageSourceRef(kind="message", message_id=A)
    ok = term(state=c.TermState.UNCLEAR, unclear_reason="relative_date", sources=[source])
    assert ok.unclear_reason == "relative_date"
    with pytest.raises(ValidationError):
        term(unclear_reason="relative_date")


def test_only_a_stated_term_can_be_confirmed() -> None:
    """Answer 4: confirming needs a concrete value; an unresolved term is not confirmed."""
    source = c.MessageSourceRef(kind="message", message_id=A)
    money = c.MoneyValue(kind="money", paise="100")
    done = term(
        state=c.TermState.STATED, value=money, sources=[source], confirmed_at=NOW, confirmed_by=A
    )
    assert done.confirmed_at == NOW
    for state in (c.TermState.UNCLEAR, c.TermState.CONTRADICTED):
        with pytest.raises(ValidationError):
            term(state=state, sources=[source], confirmed_at=NOW, confirmed_by=A)
    with pytest.raises(ValidationError):
        term(state=c.TermState.STATED, value=money, sources=[source], confirmed_at=NOW)
    with pytest.raises(ValidationError):
        term(state=c.TermState.STATED, value=money, sources=[source], confirmed_by=A)


def test_terms_use_lists_because_they_are_mutable() -> None:
    t = term()
    assert isinstance(t.sources, list) and isinstance(t.alternatives, list)


# ---- flags (answers 5 and 6) ----


def flag(sources: list[c.MessageSourceRef | c.VoiceSourceRef]) -> c.Flag:
    return c.Flag(
        id=A, deal_id=B, kind=c.FlagKind.CONTRADICTION, rule_id="text_vs_voice",
        term_key="delivery_date", reason_code="text_vs_voice", reason_params={"message": "3"},
        sources=sources, created_at=NOW, resolved_at=None,
    )  # fmt: skip


def test_cross_modal_is_derived_from_the_sources() -> None:
    text = c.MessageSourceRef(kind="message", message_id=A)
    voice = c.VoiceSourceRef(kind="voice", voice_note_id=A, start_ms=0, end_ms=10)
    assert flag([text, voice]).cross_modal is True
    assert flag([text, text]).cross_modal is False
    assert flag([voice]).cross_modal is False
    assert "cross_modal" not in c.Flag.model_fields


def test_a_flag_holds_a_reason_code_and_text_parameters_not_prose() -> None:
    assert "reason" not in c.Flag.model_fields
    assert {"reason_code", "reason_params"} <= set(c.Flag.model_fields)
    with pytest.raises(ValidationError):
        c.Flag(
            id=A, deal_id=B, kind=c.FlagKind.MISSING, rule_id="r", term_key=None,
            reason_code="term_missing", reason_params={"n": 3}, sources=[],  # type: ignore[dict-item]
            created_at=NOW, resolved_at=None,
        )  # fmt: skip


# ---- time units (D3, Q-61) ----


def test_all_times_are_integer_milliseconds() -> None:
    assert {"start_ms", "end_ms"} <= set(c.TranscriptSpan.model_fields)
    assert "duration_ms" in c.VoiceNote.model_fields
    for model in c.ALL_MODELS:
        assert not any(n.endswith("_s") for n in model.model_fields), model.__name__
    with pytest.raises(ValidationError):
        c.TranscriptSpan(start_ms=1.2, end_ms=3, text="x", confidence=0.5)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        c.TranscriptSpan(start_ms=5, end_ms=3, text="x", confidence=0.5)


# ---- recap and echo code (D1) ----


BODY = "Hi, confirming:\n50 mugs"


def recap(**kw: object) -> c.Recap:
    base: dict[str, object] = {
        "id": A, "deal_id": B, "version_n": 1, "language": c.Language.EN, "lines": (),
        "body_text": BODY, "text": BODY + "\nIf all correct, reply: CONFIRM 7F3K",
        "recap_hash": H, "echo_code": c.EchoCode(code="7F3K", recap_hash=H, version_n=1),
        "created_at": NOW,
    }  # fmt: skip
    base.update(kw)
    return c.Recap(**base)  # type: ignore[arg-type]


def test_recap_has_a_body_without_the_code_and_a_text_with_it() -> None:
    r = recap()
    assert r.text.startswith(r.body_text) and "7F3K" not in r.body_text
    assert "7F3K" in r.text


def test_recap_parts_must_be_consistent() -> None:
    with pytest.raises(ValidationError):
        recap(text="Something else CONFIRM 7F3K")
    with pytest.raises(ValidationError):
        recap(text="Hi, confirming:\n50 mugs\nno code here")
    with pytest.raises(ValidationError):
        recap(echo_code=c.EchoCode(code="7F3K", recap_hash="b" * 64, version_n=1))
    with pytest.raises(ValidationError):
        recap(echo_code=c.EchoCode(code="7F3K", recap_hash=H, version_n=2))


# ---- receipt (D2) ----


def test_receipt_is_a_body_plus_a_hash_outside_the_body() -> None:
    assert set(c.Receipt.model_fields) == {"body", "receipt_hash"}
    assert "receipt_hash" not in c.ReceiptBody.model_fields


# ---- agreed terms and versions (D5, answer 11) ----


def test_agreed_terms_are_frozen_and_need_a_full_date() -> None:
    src = (c.MessageSourceRef(kind="message", message_id=A),)
    ok = c.AgreedTerm(
        key="delivery_date", value=c.DateValue(kind="date", date="2026-11-15"), sources=src,
        confirmed_by=A, confirmed_at=NOW,
    )  # fmt: skip
    with pytest.raises(ValidationError):
        ok.key = "other"
    with pytest.raises(ValidationError):
        c.AgreedTerm(
            key="delivery_date", value=c.PartialDateValue(kind="partial_date", month_day="--11-15"),
            sources=src, confirmed_by=A, confirmed_at=NOW,
        )  # fmt: skip
    assert (
        "version_n" in c.AgreementVersion.model_fields
        and "n" not in c.AgreementVersion.model_fields
    )


def test_confirmation_carries_the_fields_the_leaf_needs() -> None:
    assert {"deal_id", "version_n", "code"} <= set(c.Confirmation.model_fields)


def test_confirmation_failure_reasons_are_the_decided_set() -> None:
    assert {f.value for f in c.ConfirmationFailure} == {
        "code_mismatch", "wrong_sender", "recap_changed", "malformed_reply", "declined",
    }  # fmt: skip


# ---- first differing item (D7) ----


def test_first_difference_names_every_leaf_type() -> None:
    kinds = set(c.FirstDifference.model_fields["kind"].annotation.__args__)  # type: ignore[union-attr]
    leaf_names = {t.value for t in c.LeafType}
    assert leaf_names <= kinds
    assert {"chain_link", "import_record"} <= kinds
    assert "other_leaf" not in kinds


# ---- leaf rows and bundles ----


def test_leaf_row_is_disclosed_all_or_nothing() -> None:
    hidden = c.LeafRow(
        seq=1,
        leaf_type=c.LeafType.MESSAGE,
        leaf_hash=H,
        salt=None,
        payload_digest=None,
        payload=None,
    )
    assert hidden.salt is None
    shown = c.LeafRow(
        seq=1,
        leaf_type=c.LeafType.MESSAGE,
        leaf_hash=H,
        salt="ab" * 16,
        payload_digest=H,
        payload="{}",
    )
    assert shown.payload == "{}"
    with pytest.raises(ValidationError):
        c.LeafRow(
            seq=1,
            leaf_type=c.LeafType.MESSAGE,
            leaf_hash=H,
            salt="ab" * 16,
            payload_digest=None,
            payload=None,
        )
    with pytest.raises(ValidationError):
        c.LeafRow(
            seq=1,
            leaf_type=c.LeafType.MESSAGE,
            leaf_hash=H,
            salt="ab" * 8,
            payload_digest=H,
            payload=None,
        )


# ---- stream envelope ----


def test_stream_events_are_discriminated_by_type() -> None:
    env = c.StreamEnvelope.model_validate_json(
        f'{{"event_id":1,"deal_id":"{A}","sent_at":"2026-10-12T10:02:00+05:30",'
        '"event":{"type":"progress","stage":"voice","done":1,"total":3}}'
    )
    assert isinstance(env.event, c.ProgressEvent)
    with pytest.raises(ValidationError):
        c.StreamEnvelope.model_validate_json(
            f'{{"event_id":1,"deal_id":"{A}","sent_at":"2026-10-12T10:02:00+05:30",'
            '"event":{"type":"nonsense"}}'
        )


def test_utc_timestamps_are_accepted_and_kept_as_given() -> None:
    value = datetime(2026, 10, 12, 4, 32, 0, tzinfo=UTC)
    anchor = c.Anchor(network="n", tx="t", block_time=value)
    assert anchor.block_time.utcoffset() == timedelta(0)
