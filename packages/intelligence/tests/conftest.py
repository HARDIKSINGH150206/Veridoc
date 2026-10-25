"""Fixtures for the model adapter tests."""

import pytest

from packages.intelligence.tests.chat_builders import ChatBuilder


@pytest.fixture
def chat() -> ChatBuilder:
    return ChatBuilder()


@pytest.fixture
def mixed_chat(chat: ChatBuilder) -> ChatBuilder:
    """Positions: 1 text, 2 system, 3 media omitted, 4 deleted, 5 voice note, 6 text."""
    chat.say("Raju", "200 shirts, 480 each ok?")
    chat.say("Raju", "Messages and calls are end-to-end encrypted.", system=True)
    chat.say("Meena", "<Media omitted>", attachment="b" * 64)
    chat.say("Raju", "This message was deleted")
    chat.voice_note(
        "Meena",
        [(0, 2400, "okay I will send the advance"), (2400, 5100, "forty eight thousand today")],
    )
    chat.say("Raju", "advance 48000 received, delivery on 15 November")
    return chat
