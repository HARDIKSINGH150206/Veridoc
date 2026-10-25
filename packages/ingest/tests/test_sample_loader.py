"""Bundled sample metadata and the loader used by the walking skeleton (issue #29)."""

import json
from pathlib import Path

import pytest

from packages.contracts import ParticipantRole
from packages.ingest.samples import SampleNotFound, SampleUnavailable, list_samples, load_sample

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
SAMPLES = ("ambiguous", "clean", "contradictory")


def test_the_three_bundled_samples_are_listed_in_order() -> None:
    assert list_samples(FIXTURES) == list(SAMPLES)


@pytest.mark.parametrize("sample", SAMPLES)
def test_sample_has_two_party_participants_matching_the_export(sample: str) -> None:
    loaded = load_sample(sample, FIXTURES)
    names = [line.split(" - ", 1)[1].split(": ", 1)[0] for line in
             (FIXTURES / f"{sample}.txt").read_text("utf-8").splitlines()]  # fmt: skip
    assert {p.display_name for p in loaded.participants} == set(names)
    assert len({p.id for p in loaded.participants}) == len(loaded.participants) == 2
    assert all(p.role is ParticipantRole.PARTY for p in loaded.participants)
    assert sum(p.is_me for p in loaded.participants) == 1


@pytest.mark.parametrize("sample", SAMPLES)
def test_every_message_is_sent_by_a_listed_participant(sample: str) -> None:
    loaded = load_sample(sample, FIXTURES)
    ids = {p.id for p in loaded.participants}
    assert loaded.messages and {m.sender_id for m in loaded.messages} <= ids
    by_id = {p.id: p.display_name for p in loaded.participants}
    lines = (FIXTURES / f"{sample}.txt").read_text("utf-8").splitlines()
    for message, line in zip(loaded.messages, lines, strict=True):
        assert by_id[message.sender_id] == line.split(" - ", 1)[1].split(": ", 1)[0]


@pytest.mark.parametrize("sample", SAMPLES)
def test_sample_names_its_playbook(sample: str) -> None:
    assert load_sample(sample, FIXTURES).playbook_id == "supply_order"


def test_unknown_sample_is_not_found() -> None:
    for name in ("nope", "../clean", "clean.json", "meta/clean"):
        with pytest.raises(SampleNotFound):
            load_sample(name, FIXTURES)


def test_missing_or_corrupt_metadata_fails_closed(tmp_path: Path) -> None:
    messages = tmp_path / "messages"
    messages.mkdir()
    (tmp_path / "meta").mkdir()
    source = json.loads((FIXTURES / "messages" / "clean.json").read_text("utf-8"))
    (messages / "clean.json").write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(SampleUnavailable, match="Sample data unavailable"):
        load_sample("clean", tmp_path)  # no metadata file
    (tmp_path / "meta" / "clean.json").write_text('{"playbook_id": 1}', encoding="utf-8")
    with pytest.raises(SampleUnavailable, match="Sample data unavailable"):
        load_sample("clean", tmp_path)
