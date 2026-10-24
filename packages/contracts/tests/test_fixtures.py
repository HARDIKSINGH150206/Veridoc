"""The sample deals in packages/contracts/fixtures/ must validate against the models."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

import packages.contracts as c

FIXTURES = Path(c.__file__).resolve().parent / "fixtures"
DEALS = sorted(FIXTURES.glob("*.deal.json"))
SECTIONS: dict[str, type[BaseModel]] = {
    "participants": c.Participant,
    "messages": c.Message,
    "voice_notes": c.VoiceNote,
    "terms": c.Term,
    "flags": c.Flag,
    "suggestions": c.Suggestion,
    "handshake_questions": c.HandshakeQuestion,
    "sealed_answers": c.SealedAnswers,
    "recaps": c.Recap,
    "confirmations": c.Confirmation,
    "versions": c.AgreementVersion,
    "version_diffs": c.VersionDiff,
    "receipts": c.Receipt,
    "verify_results": c.VerifyResult,
    "dispute_packs": c.DisputePackManifest,
}


def load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def parsed(path: Path) -> dict[str, list[BaseModel]]:
    data = load(path)
    out: dict[str, list[BaseModel]] = {
        name: [model.model_validate_json(json.dumps(item)) for item in data[name]]
        for name, model in SECTIONS.items()
    }
    out["score"] = [c.EvidenceScore.model_validate_json(json.dumps(data["score"]))]
    out["playbook"] = [c.PlaybookRef.model_validate_json(json.dumps(data["playbook"]))]
    return out


def test_the_three_sample_deals_exist() -> None:
    assert [p.name for p in DEALS] == [
        "ambiguous.deal.json",
        "clean.deal.json",
        "contradictory.deal.json",
    ]


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_every_section_validates_against_its_model(path: Path) -> None:
    assert parsed(path)


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
    for message in data["messages"]:
        assert message["sender_id"] in participant_ids
    for answers in data["sealed_answers"]:
        assert answers["party_id"] in participant_ids


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_score_points_add_up_to_the_total(path: Path) -> None:
    """Sanity check of the fixture only. The formula itself lives in packages/intelligence."""
    score = parsed(path)["score"][0]
    assert isinstance(score, c.EvidenceScore)
    assert round(sum(item.points for item in score.breakdown)) == score.total


@pytest.mark.parametrize("path", DEALS, ids=lambda p: p.name)
def test_only_confirmed_terms_are_in_versions(path: Path) -> None:
    for version in parsed(path)["versions"]:
        assert isinstance(version, c.AgreementVersion)
        assert all(term.confirmed_at is not None for term in version.terms)


def test_the_fixtures_cover_the_main_cases() -> None:
    everything = {p.name: parsed(p) for p in DEALS}
    terms = [t for d in everything.values() for t in d["terms"] if isinstance(t, c.Term)]
    assert {t.state for t in terms} == set(c.TermState)
    flags = [f for d in everything.values() for f in d["flags"] if isinstance(f, c.Flag)]
    assert {f.kind for f in flags} >= {
        c.FlagKind.AMBIGUOUS,
        c.FlagKind.MISSING,
        c.FlagKind.CONTRADICTION,
        c.FlagKind.NEEDS_REVIEW,
    }
    verdicts = {v.verdict for d in everything.values() for v in d["verify_results"]}  # type: ignore[attr-defined]
    assert verdicts == set(c.Verdict)
    sources = [s for t in terms for s in t.sources] + [s for f in flags for s in f.sources]
    assert any(isinstance(s, c.VoiceSourceRef) for s in sources)
    assert any(isinstance(s, c.MessageSourceRef) for s in sources)
    confirmed = [
        x
        for d in everything.values()
        for x in d["confirmations"]
        if isinstance(x, c.Confirmation) and x.state is c.ConfirmationState.CONFIRMED
    ]
    assert confirmed


def test_fixtures_use_obviously_fake_hashes() -> None:
    """Hashes in fixtures are placeholders (leading zeros), never computed evidence."""
    for path in DEALS:
        text = path.read_text(encoding="utf-8")
        assert "Hashes are fake placeholders" in text
