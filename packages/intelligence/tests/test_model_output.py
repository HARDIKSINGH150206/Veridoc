"""ModelOutput matches the local model's JSON (LLM_HANDOVER.md section 5) and parses safely."""

import json
from pathlib import Path
from typing import Any

import pytest

from packages.intelligence.model_adapter import (
    MalformedTerm,
    ModelOutput,
    ModelOutputError,
    TermOutput,
    parse_model_output,
)

RECORDINGS = Path(__file__).resolve().parents[1] / "fixtures" / "recordings"

FULL: dict[str, Any] = {
    "deal_type": "supply_order",
    "terms": {
        "buyer": {"status": "stated", "value": "Raju", "quote": ["Raju"], "msg": [1]},
        "total_amount": {"status": "missing"},
        "delivery_date": {
            "status": "unclear",
            "value": None,
            "quote": ["delivery next week"],
            "msg": [2],
            "reason": "relative_date",
        },
        "unit_price": {"status": "contradicted", "value": None, "quote": ["a", "b"], "msg": [1, 3]},
    },
}


def test_the_handover_shape_parses_and_missing_is_just_a_status() -> None:
    output = parse_model_output(json.dumps(FULL))
    assert output.deal_type == "supply_order"
    buyer = output.terms["buyer"]
    assert isinstance(buyer, TermOutput) and buyer.value == "Raju" and buyer.msg == [1]
    missing = output.terms["total_amount"]
    assert isinstance(missing, TermOutput)
    assert (missing.status, missing.value, missing.quote, missing.msg, missing.reason) == (
        "missing", None, [], [], None,
    )  # fmt: skip
    unclear = output.terms["delivery_date"]
    assert isinstance(unclear, TermOutput) and unclear.reason == "relative_date"


def test_model_output_round_trips_to_the_same_json() -> None:
    output = parse_model_output(json.dumps(FULL))
    dumped = json.loads(output.model_dump_json(exclude_defaults=True))
    assert dumped["terms"]["total_amount"] == {"status": "missing"}
    assert dumped["terms"]["buyer"] == FULL["terms"]["buyer"]


def test_a_malformed_single_term_is_kept_as_malformed_not_raised() -> None:
    raw = {**FULL["terms"], "quantity": {"status": "stated", "value": 200, "quote": "200 shirts"}}
    output = parse_model_output(json.dumps({"deal_type": "supply_order", "terms": raw}))
    bad = output.terms["quantity"]
    assert isinstance(bad, MalformedTerm)
    assert "200 shirts" in bad.raw
    assert isinstance(output.terms["buyer"], TermOutput)


@pytest.mark.parametrize(
    "term",
    [
        "stated",
        ["stated"],
        {"value": 5},
        {"status": 5},
        {"status": "stated", "value": True},
        {"status": "stated", "value": [1]},
        {"status": "stated", "msg": ["1"]},
        {"status": "stated", "extra": 1},
        {"status": "unclear", "reason": 7},
        None,
    ],
)
def test_term_shapes_that_do_not_match_become_malformed(term: object) -> None:
    output = parse_model_output(json.dumps({"deal_type": "x", "terms": {"k": term}}))
    assert isinstance(output.terms["k"], MalformedTerm)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "not json",
        "[]",
        "null",
        '{"terms": {}}',
        '{"deal_type": "x"}',
        '{"deal_type": 1, "terms": {}}',
        '{"deal_type": "x", "terms": []}',
        "```json\n{}\n```",
    ],
)
def test_output_that_is_not_the_expected_object_raises_model_output_error(text: str) -> None:
    with pytest.raises(ModelOutputError):
        parse_model_output(text)


def test_model_output_error_is_a_value_error() -> None:
    assert issubclass(ModelOutputError, ValueError)


def test_the_recorded_real_output_parses() -> None:
    recorded = json.loads((RECORDINGS / "raju-meena-v1.json").read_text(encoding="utf-8"))
    output = ModelOutput.model_validate(recorded["output"])
    assert set(output.terms) >= {"unit_price", "advance_amount", "buyer"}
