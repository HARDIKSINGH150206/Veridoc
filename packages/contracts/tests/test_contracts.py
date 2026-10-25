"""Property tests that apply to every contract model."""

import re
from pathlib import Path

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

import packages.contracts as contracts
from packages.contracts import ALL_MODELS, CONTRACTS_VERSION, UNION_TYPES

PACKAGE = Path(contracts.__file__).resolve().parent
REQUIREMENT_ID = re.compile(r"^(FR|NFR)-[A-Z0-9]+-\d{3}$")
UUID_A = "11111111-1111-4111-8111-111111111111"
UUID_B = "22222222-2222-4222-8222-222222222222"
HASH = "a" * 64
MUTABLE = {"Term", "Flag", "Suggestion"}
EXPECTED = {
    "Participant", "Message", "VoiceNote", "TranscriptSpan", "Transcript", "MessageSourceRef",
    "VoiceSourceRef", "PlaybookRef", "MoneyValue", "QuantityValue", "DateValue",
    "PartialDateValue", "EventValue", "DurationValue", "TextValue", "Term", "AlternativeValue",
    "Flag", "EvidenceScore", "ScoreBreakdownItem", "Suggestion", "HandshakeQuestion",
    "HandshakeAnswer", "SealedAnswers", "HandshakeRevealRow", "HandshakeReveal", "Recap",
    "RecapLine", "EchoCode", "Confirmation", "AgreedTerm", "AgreementVersion", "VersionDiff",
    "TermDiffRow", "ChainLink", "Anchor", "ReceiptBody", "Receipt", "VerifyResult", "VerifyCheck",
    "FirstDifference", "DisputePackManifest", "PackPart", "ImportRecord", "LeafRow", "BundleFile",
    "ReceiptBundle", "ErrorBody", "TermEvent", "FlagEvent", "ScoreEvent", "SuggestionEvent",
    "ProgressEvent", "DoneEvent", "ErrorEvent", "StreamEnvelope", "DealSummary",
}  # fmt: skip


def test_every_expected_model_is_exported_exactly_once() -> None:
    names = [m.__name__ for m in ALL_MODELS]
    assert set(names) == EXPECTED
    assert len(names) == len(set(names))


def test_the_discriminated_unions_are_exported() -> None:
    assert set(UNION_TYPES) == {"SourceRef", "TermValue", "StreamEvent"}


def test_version_constant_is_semver_and_in_changelog() -> None:
    assert CONTRACTS_VERSION == "0.2.0"
    assert re.fullmatch(r"\d+\.\d+\.\d+", CONTRACTS_VERSION)
    changelog = (PACKAGE / "CHANGELOG.md").read_text(encoding="utf-8")
    assert changelog.index(f"## {CONTRACTS_VERSION}") < changelog.index("## 0.1.0")


@pytest.mark.parametrize("model", ALL_MODELS, ids=lambda m: m.__name__)
def test_model_has_docstring_with_requirements(model: type[BaseModel]) -> None:
    doc = model.__doc__ or ""
    assert len(doc.strip()) > 20, "docstring missing"
    extra = model.model_config.get("json_schema_extra")
    assert isinstance(extra, dict)
    reqs = extra["requirements"]
    assert isinstance(reqs, list) and reqs
    for req in reqs:
        assert isinstance(req, str)
        assert REQUIREMENT_ID.match(req), req
        assert req in doc, f"{req} must also appear in the docstring of {model.__name__}"


@pytest.mark.parametrize("model", ALL_MODELS, ids=lambda m: m.__name__)
def test_every_field_has_a_description(model: type[BaseModel]) -> None:
    for name, field in model.model_fields.items():
        assert field.description, f"{model.__name__}.{name} has no description"


@pytest.mark.parametrize("model", ALL_MODELS, ids=lambda m: m.__name__)
def test_models_are_strict_and_forbid_extra_fields(model: type[BaseModel]) -> None:
    assert model.model_config.get("strict") is True
    assert model.model_config.get("extra") == "forbid"


@pytest.mark.parametrize("model", ALL_MODELS, ids=lambda m: m.__name__)
def test_json_schema_can_be_generated(model: type[BaseModel]) -> None:
    schema = model.model_json_schema()
    assert schema["title"] == model.__name__
    assert schema["requirements"]


@pytest.mark.parametrize("name", sorted(UNION_TYPES))
def test_union_schemas_can_be_generated(name: str) -> None:
    schema = TypeAdapter(UNION_TYPES[name]).json_schema()
    assert "oneOf" in schema or "anyOf" in schema


def test_only_term_flag_and_suggestion_are_mutable() -> None:
    for model in ALL_MODELS:
        is_frozen = model.model_config.get("frozen") is True
        assert is_frozen == (model.__name__ not in MUTABLE), model.__name__


def test_frozen_model_cannot_be_changed() -> None:
    ref = contracts.PlaybookRef(key="supply_order", version=1)
    with pytest.raises(ValidationError):
        ref.version = 2


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        contracts.PlaybookRef.model_validate({"key": "k", "version": 1, "surprise": True})


def test_strict_mode_does_not_coerce_types() -> None:
    with pytest.raises(ValidationError):
        contracts.PlaybookRef.model_validate({"key": "k", "version": "1"})


def test_hashes_must_be_lowercase_sha256_hex() -> None:
    contracts.EchoCode(code="7F3K", recap_hash=HASH, version_n=1)
    for bad in ("A" * 64, "a" * 63, "g" * 64, ""):
        with pytest.raises(ValidationError):
            contracts.EchoCode(code="7F3K", recap_hash=bad, version_n=1)


def test_echo_code_is_four_crockford_characters() -> None:
    for bad in ("7F3", "7F3KK", "7F3I", "7f3k", "7F3U"):
        with pytest.raises(ValidationError):
            contracts.EchoCode(code=bad, recap_hash=HASH, version_n=1)


UPPER = "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"


@pytest.mark.parametrize("bad", ["not-a-uuid", UPPER, UUID_A[:-1], "", UUID_A + "0"])
def test_ids_must_be_lowercase_uuids(bad: str) -> None:
    with pytest.raises(ValidationError):
        contracts.MessageSourceRef(kind="message", message_id=bad)


def test_source_ref_is_message_or_voice_with_millisecond_times() -> None:
    adapter = TypeAdapter(contracts.SourceRef)
    msg = adapter.validate_python({"kind": "message", "message_id": UUID_A})
    assert isinstance(msg, contracts.MessageSourceRef)
    voice = adapter.validate_python(
        {"kind": "voice", "voice_note_id": UUID_A, "start_ms": 1000, "end_ms": 3500}
    )
    assert isinstance(voice, contracts.VoiceSourceRef)
    with pytest.raises(ValidationError):
        adapter.validate_python({"kind": "voice", "voice_note_id": UUID_A, "start_ms": 1000})
    with pytest.raises(ValidationError):
        adapter.validate_python(
            {"kind": "voice", "voice_note_id": UUID_A, "start_ms": 5000, "end_ms": 2000}
        )
    with pytest.raises(ValidationError):
        adapter.validate_python(  # seconds as a float are not allowed any more
            {"kind": "voice", "voice_note_id": UUID_A, "start_ms": 1.5, "end_ms": 3.5}
        )


def message_json(ts: str) -> str:
    return (
        f'{{"id":"{UUID_A}","deal_id":"{UUID_B}","seq":1,"sender_id":"{UUID_B}","ts":"{ts}",'
        '"text":"hi","attachment_hash":null,"is_system":false,"origin":"export"}'
    )


def test_timestamps_need_an_offset_and_whole_seconds() -> None:
    contracts.Message.model_validate_json(message_json("2026-10-12T10:02:00+05:30"))
    contracts.Message.model_validate_json(message_json("2026-10-12T04:32:00Z"))
    for bad in ("2026-10-12T10:02:00", "2026-10-12T10:02:00.5+05:30"):
        with pytest.raises(ValidationError):
            contracts.Message.model_validate_json(message_json(bad))


def test_no_model_hardcodes_playbook_values() -> None:
    """Weights and thresholds belong in playbooks and config, not in contract defaults."""
    for model in ALL_MODELS:
        for name, field in model.model_fields.items():
            if name in {"weight", "threshold", "points"}:
                assert field.is_required(), f"{model.__name__}.{name} must not have a default"
