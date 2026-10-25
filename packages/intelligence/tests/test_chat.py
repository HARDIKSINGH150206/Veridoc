"""The numbered chat is built from the same message list the mapping uses."""

from packages.intelligence.model_adapter import numbered_chat, prompt_format
from packages.intelligence.tests.chat_builders import ChatBuilder


def test_every_message_gets_a_line_in_order_including_odd_lines(mixed_chat: ChatBuilder) -> None:
    lines = numbered_chat(mixed_chat.context()).split("\n")
    assert len(lines) == 6
    assert lines[0] == "[1] Raju: 200 shirts, 480 each ok?"
    assert lines[1].startswith(f"[2] {prompt_format().system_sender}: ")
    assert lines[2] == "[3] Meena: <Media omitted>"
    assert lines[3] == "[4] Raju: This message was deleted"
    assert lines[5] == "[6] Raju: advance 48000 received, delivery on 15 November"


def test_a_voice_note_line_carries_its_transcript_text(mixed_chat: ChatBuilder) -> None:
    line = numbered_chat(mixed_chat.context()).split("\n")[4]
    assert line == "[5] Meena: okay I will send the advance forty eight thousand today"


def test_a_voice_note_without_a_transcript_keeps_its_message_text(chat: ChatBuilder) -> None:
    chat.say("Meena", "<attached: voice.opus>", attachment="c" * 64)
    assert numbered_chat(chat.context()) == "[1] Meena: <attached: voice.opus>"


def test_line_breaks_inside_a_message_do_not_split_the_numbering(chat: ChatBuilder) -> None:
    chat.say("Raju", "first line\nsecond line")
    chat.say("Meena", "ok")
    assert numbered_chat(chat.context()).split("\n") == [
        "[1] Raju: first line second line",
        "[2] Meena: ok",
    ]
