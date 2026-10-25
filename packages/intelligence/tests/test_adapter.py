"""ModelAdapter protocol, FakeModelAdapter, the mode switch and the AI/hash-path boundary."""

import json
from pathlib import Path

import pytest

from packages.intelligence import model_adapter as ma
from packages.intelligence.model_adapter import (
    FakeModelAdapter,
    LocalModelAdapter,
    ModelAdapter,
    ModelOutput,
    TermOutput,
    UnrecordedChat,
    build_adapter,
    load_recordings,
    numbered_chat,
)
from packages.intelligence.tests.chat_builders import ChatBuilder

RECORDINGS = Path(__file__).resolve().parents[1] / "fixtures" / "recordings"
RECORDING = json.loads((RECORDINGS / "raju-meena-v1.json").read_text(encoding="utf-8"))


def test_fake_adapter_returns_the_recorded_output_for_the_recorded_chat() -> None:
    fake = FakeModelAdapter(load_recordings(RECORDINGS))
    output = fake.extract(RECORDING["numbered_chat"], RECORDING["playbook_id"])
    assert output == ModelOutput.model_validate(RECORDING["output"])


def test_fake_adapter_keeps_the_two_known_real_mistakes() -> None:
    output = FakeModelAdapter(load_recordings(RECORDINGS)).extract(
        RECORDING["numbered_chat"], RECORDING["playbook_id"]
    )
    unit_price = output.terms["unit_price"]
    assert isinstance(unit_price, TermOutput)
    assert unit_price.value == 48000 and unit_price.quote == ["480 each ok?"]  # quote says 480
    advance = output.terms["advance_amount"]
    assert isinstance(advance, TermOutput)
    assert advance.status == "unclear" and advance.msg == [
        3
    ]  # message 4 ("done sent 48000") missed
    assert "done sent 48000" in RECORDING["numbered_chat"]


def test_the_recorded_chat_is_what_numbered_chat_builds(chat: ChatBuilder) -> None:
    builder = chat
    builder.say("Raju", "200 shirts, 480 each ok?")
    builder.say("Meena", "ok. delivery next week")
    builder.say("Raju", "advance half now")
    builder.say("Meena", "done sent 48000")
    assert numbered_chat(builder.context()) == RECORDING["numbered_chat"]


def test_unrecorded_chat_or_playbook_raises_unrecorded_chat() -> None:
    fake = FakeModelAdapter(load_recordings(RECORDINGS))
    with pytest.raises(UnrecordedChat):
        fake.extract("[1] Raju: something else", RECORDING["playbook_id"])
    with pytest.raises(UnrecordedChat):
        fake.extract(RECORDING["numbered_chat"], "freelance")


def test_adapters_satisfy_the_protocol() -> None:
    assert isinstance(FakeModelAdapter(()), ModelAdapter)
    assert isinstance(LocalModelAdapter(), ModelAdapter)


def test_build_adapter_fake_and_local() -> None:
    assert isinstance(build_adapter("fake", RECORDINGS), FakeModelAdapter)
    local = build_adapter("local", RECORDINGS)
    assert isinstance(local, LocalModelAdapter)
    with pytest.raises(NotImplementedError, match="local"):
        local.extract("[1] a: b", "supply_order")


def test_build_adapter_rejects_an_unknown_mode() -> None:
    with pytest.raises(ValueError, match="mode"):
        build_adapter("cloud", RECORDINGS)


def test_load_recordings_ignores_nothing_and_rejects_a_bad_file(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text('{"playbook_id": "x"}', encoding="utf-8")
    with pytest.raises(ValueError, match="bad.json"):
        load_recordings(tmp_path)


def test_the_adapter_never_reaches_the_hash_path_or_the_vault() -> None:
    package = Path(ma.__file__).parent
    for source in package.glob("*.py"):
        text = source.read_text(encoding="utf-8")
        assert "packages.vault" not in text, source.name
        assert "packages.integrity" not in text, source.name
        assert "hashlib" not in text, source.name
