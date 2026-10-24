"""Property tests that apply to every contract model (written before the models)."""

import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

import packages.contracts as contracts
from packages.contracts import ALL_MODELS, CONTRACTS_VERSION

PACKAGE = Path(contracts.__file__).resolve().parent
REQUIREMENT_ID = re.compile(r"^(FR|NFR)-[A-Z0-9]+-\d{3}$|^(FR|NFR)-[A-Z0-9]+-\*$")
EXPECTED = {
    "Participant", "Message", "VoiceNote", "TranscriptSpan", "Transcript", "SourceRef",
    "MessageSourceRef", "VoiceSourceRef", "Term", "AlternativeValue", "Flag", "EvidenceScore",
    "ScoreBreakdownItem", "Suggestion", "HandshakeQuestion", "HandshakeAnswer", "SealedAnswers",
    "Recap", "RecapLine", "EchoCode", "Confirmation", "AgreementVersion", "VersionDiff",
    "TermDiffRow", "ChainLink", "Anchor", "Receipt", "VerifyResult", "VerifyCheck",
    "FirstDifference", "DisputePackManifest", "PackPart", "PlaybookRef",
}  # fmt: skip


def concrete_models() -> Iterator[type[BaseModel]]:
    yield from ALL_MODELS


def test_every_expected_model_is_exported() -> None:
    assert {m.__name__ for m in ALL_MODELS} >= EXPECTED - {"SourceRef"}
    assert hasattr(contracts, "SourceRef")


def test_version_constant_is_semver_and_in_changelog() -> None:
    assert CONTRACTS_VERSION == "0.1.0"
    assert re.fullmatch(r"\d+\.\d+\.\d+", CONTRACTS_VERSION)
    changelog = (PACKAGE / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {CONTRACTS_VERSION}" in changelog


@pytest.mark.parametrize("model", list(concrete_models()), ids=lambda m: m.__name__)
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


@pytest.mark.parametrize("model", list(concrete_models()), ids=lambda m: m.__name__)
def test_every_field_has_a_description(model: type[BaseModel]) -> None:
    for name, field in model.model_fields.items():
        assert field.description, f"{model.__name__}.{name} has no description"


@pytest.mark.parametrize("model", list(concrete_models()), ids=lambda m: m.__name__)
def test_models_are_strict_and_forbid_extra_fields(model: type[BaseModel]) -> None:
    assert model.model_config.get("strict") is True
    assert model.model_config.get("extra") == "forbid"


@pytest.mark.parametrize("model", list(concrete_models()), ids=lambda m: m.__name__)
def test_json_schema_can_be_generated(model: type[BaseModel]) -> None:
    schema = model.model_json_schema()
    assert schema["title"] == model.__name__
    assert schema["requirements"]


def test_immutable_records_are_frozen() -> None:
    frozen = {
        "Participant", "Message", "VoiceNote", "TranscriptSpan", "Transcript", "MessageSourceRef",
        "VoiceSourceRef", "AlternativeValue", "EvidenceScore", "ScoreBreakdownItem",
        "HandshakeQuestion", "HandshakeAnswer", "SealedAnswers", "Recap", "RecapLine", "EchoCode",
        "AgreementVersion", "VersionDiff", "TermDiffRow", "ChainLink", "Anchor", "Receipt",
        "VerifyResult", "VerifyCheck", "FirstDifference", "PackPart", "PlaybookRef", "Confirmation",
        "DisputePackManifest",
    }  # fmt: skip
    for model in ALL_MODELS:
        is_frozen = model.model_config.get("frozen") is True
        assert is_frozen == (model.__name__ in frozen), model.__name__


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
    good = "a" * 64
    contracts.EchoCode(code="7F3K", recap_hash=good, version_n=1)
    for bad in ("A" * 64, "a" * 63, "g" * 64, ""):
        with pytest.raises(ValidationError):
            contracts.EchoCode(code="7F3K", recap_hash=bad, version_n=1)


def test_echo_code_is_four_crockford_characters() -> None:
    good = "a" * 64
    for bad in ("7F3", "7F3KK", "7F3I", "7f3k", "7F3U"):
        with pytest.raises(ValidationError):
            contracts.EchoCode(code=bad, recap_hash=good, version_n=1)


def test_source_ref_is_message_or_voice_with_times() -> None:
    from pydantic import TypeAdapter

    adapter = TypeAdapter(contracts.SourceRef)
    msg = adapter.validate_python({"kind": "message", "message_id": "m1"})
    assert isinstance(msg, contracts.MessageSourceRef)
    voice = adapter.validate_python(
        {"kind": "voice", "voice_note_id": "v1", "start_s": 1.0, "end_s": 3.5}
    )
    assert isinstance(voice, contracts.VoiceSourceRef)
    with pytest.raises(ValidationError):
        adapter.validate_python({"kind": "voice", "voice_note_id": "v1", "start_s": 1.0})
    with pytest.raises(ValidationError):
        adapter.validate_python(
            {"kind": "voice", "voice_note_id": "v1", "start_s": 5.0, "end_s": 2.0}
        )


def test_timestamps_must_carry_a_timezone() -> None:
    base = {
        "id": "m1", "deal_id": "d1", "seq": 1, "sender_id": "p1", "text": "hi",
        "attachment_hash": None, "is_system": False, "origin": "export",
    }  # fmt: skip
    contracts.Message.model_validate_json(
        '{"id":"m1","deal_id":"d1","seq":1,"sender_id":"p1","ts":"2026-10-12T10:02:00+05:30",'
        '"text":"hi","attachment_hash":null,"is_system":false,"origin":"export"}'
    )
    with pytest.raises(ValidationError):
        contracts.Message.model_validate_json(
            '{"id":"m1","deal_id":"d1","seq":1,"sender_id":"p1","ts":"2026-10-12T10:02:00",'
            '"text":"hi","attachment_hash":null,"is_system":false,"origin":"export"}'
        )
    assert base["id"] == "m1"


def test_no_model_hardcodes_playbook_values() -> None:
    """Weights and thresholds belong in playbooks and config, not in contract defaults."""
    for model in ALL_MODELS:
        for name, field in model.model_fields.items():
            if name in {"weight", "threshold", "points"}:
                assert field.is_required(), f"{model.__name__}.{name} must not have a default"
