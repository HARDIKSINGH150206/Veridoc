"""Guard the raw synthetic inputs for #12 (FR-IMP-007, FR-VOI-001).

These checks describe fixture content, not parser or analysis correctness. Contract-shaped
Message fixtures follow in #13; extraction and speech belong to Area 2.
"""

import re
import struct
import wave
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
CHATS = ("clean", "ambiguous", "contradictory")


@pytest.mark.parametrize("scenario", CHATS)
def test_chat_is_readable_export_with_two_fictional_participants(scenario: str) -> None:
    text = (FIXTURES / f"{scenario}.txt").read_text(encoding="utf-8-sig")
    assert "\ufffd" not in text
    assert "₹" in text
    # Only the deliberately simple fixture headers are checked here, not general WhatsApp input.
    lines = text.splitlines()
    headers = [re.fullmatch(r"25/10/2026, 10:\d{2} - (Asha|Bilal): (.+)", line) for line in lines]
    assert len(lines) >= 5
    assert all(headers), "Each fixture line must have its documented Android export header"
    assert {header[1] for header in headers if header} == {"Asha", "Bilal"}


def test_clean_sample_explicitly_agrees_each_required_term() -> None:
    text = (FIXTURES / "clean.txt").read_text(encoding="utf-8")
    for term in (
        "200 cotton shirts",
        "₹480 each",
        "total ₹96,000",
        "₹48,000 advance",
        "15 November 2026",
        "₹48,000 balance on delivery",
        "no late penalty",
    ):
        assert term in text
    assert "Bilal: Agreed to all those terms" in text
    assert "Asha: Agreed. Payment received" in text


def test_ambiguous_sample_leaves_delivery_unresolved_and_payment_and_penalty_absent() -> None:
    text = (FIXTURES / "ambiguous.txt").read_text(encoding="utf-8").lower()
    assert "delivery next week" in text
    assert "200 cotton shirts" in text
    assert "₹480 each" in text
    assert "₹48,000 advance" in text
    for resolved_or_missing_term in ("november", "balance", "final payment", "penalty"):
        assert resolved_or_missing_term not in text


def test_contradictory_sample_keeps_both_prices_and_references_voice() -> None:
    text = (FIXTURES / "contradictory.txt").read_text(encoding="utf-8")
    assert "total price is ₹50,000" in text
    assert "total price is ₹45,000" in text
    assert "15 November 2026" in text
    assert "<attached: delivery-22-nov.wav>" in text
    assert "We have not agreed which price or delivery date applies yet" in text


def test_voice_script_states_the_conflicting_date() -> None:
    transcript = (FIXTURES / "delivery-22-nov.transcript.txt").read_text(encoding="utf-8")
    assert "twenty-second of November, twenty twenty-six" in transcript
    assert "fifteenth" not in transcript
    assert "fifteen" not in transcript


def test_voice_fixture_is_non_silent_complete_pcm_audio() -> None:
    with wave.open(str(FIXTURES / "delivery-22-nov.wav"), "rb") as audio:
        assert audio.getcomptype() == "NONE"
        assert audio.getnchannels() == 1
        assert audio.getsampwidth() == 2
        assert audio.getframerate() == 16000
        frame_count = audio.getnframes()
        assert 1 < frame_count / audio.getframerate() < 60
        pcm = audio.readframes(frame_count)
    assert len(pcm) == frame_count * 2, "Truncated audio fixture"
    samples = [value for (value,) in struct.iter_unpack("<h", pcm)]
    assert any(value > 0 for value in samples)
    assert any(value < 0 for value in samples)
    assert len(set(samples)) > 100, "Expected speech, not silence or a constant tone"
