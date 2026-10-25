"""Adapter between the local term-extraction model and the shared contracts (Area 2)."""

from .adapter import (
    FakeModelAdapter,
    LocalModelAdapter,
    ModelAdapter,
    Recording,
    UnrecordedChat,
    build_adapter,
    load_recordings,
)
from .chat import ChatContext, VoiceEvidence, locate_in_voice, numbered_chat
from .mapping import map_output
from .output import (
    MalformedTerm,
    ModelOutput,
    ModelOutputError,
    TermOutput,
    output_from_object,
    parse_model_output,
)
from .rules import prompt_format, term_rules

__all__ = [
    "ChatContext",
    "FakeModelAdapter",
    "LocalModelAdapter",
    "MalformedTerm",
    "ModelAdapter",
    "ModelOutput",
    "ModelOutputError",
    "Recording",
    "TermOutput",
    "UnrecordedChat",
    "VoiceEvidence",
    "build_adapter",
    "load_recordings",
    "locate_in_voice",
    "map_output",
    "numbered_chat",
    "output_from_object",
    "parse_model_output",
    "prompt_format",
    "term_rules",
]
