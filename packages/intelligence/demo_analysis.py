"""Demo analysis for the walking skeleton (issue #30): a sample chat in, unconfirmed Terms out.

The numbered chat is built from the sample's own message list and the model adapter's reply is
mapped with that same list (see model_adapter/). Every term is proposed by the AI and unconfirmed;
nothing here touches the vault or the hash path.
"""

from packages.contracts import Term
from packages.ingest.samples import Sample
from packages.intelligence.model_adapter import (
    ChatContext,
    ModelAdapter,
    map_output,
    numbered_chat,
)


def chat_context(sample: Sample) -> ChatContext:
    """The chat as the model reads it. Voice notes of the samples are not transcribed here."""
    return ChatContext(
        deal_id=sample.messages[0].deal_id,
        messages=sample.messages,
        participants={p.id: p.display_name for p in sample.participants},
        voice={},
    )


def analyze_demo(sample: Sample, adapter: ModelAdapter) -> list[Term]:
    """Ask the adapter about the sample's chat and map its answer to Terms."""
    chat = chat_context(sample)
    output = adapter.extract(numbered_chat(chat), sample.playbook_id)
    return map_output(output, chat)
