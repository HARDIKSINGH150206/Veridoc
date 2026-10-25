"""The local model's JSON (LLM_HANDOVER.md section 5), as typed models, and a safe parser.

A single term that does not fit the shape is kept as a MalformedTerm so the mapping can mark it
for review. Only output that is not the expected top-level object raises ModelOutputError.
"""

import json

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ModelOutputError(ValueError):
    """The reply is not a JSON object with a deal_type and a terms object."""


class TermOutput(BaseModel):
    """One term as the model returns it. A missing term is just {"status": "missing"}.

    `status` is a plain string here: the mapping decides what to do with a status outside
    stated, unclear, contradicted and missing.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: str
    value: int | float | str | None = None
    quote: list[str] = Field(default_factory=list)
    msg: list[int] = Field(default_factory=list)
    reason: str | None = None


class MalformedTerm(BaseModel):
    """A term whose JSON did not fit TermOutput. `raw` is that JSON text, for review."""

    model_config = ConfigDict(frozen=True)

    raw: str


class ModelOutput(BaseModel):
    """The whole reply: the deal type and one entry per playbook term."""

    model_config = ConfigDict(frozen=True)

    deal_type: str
    terms: dict[str, TermOutput | MalformedTerm]


def output_from_object(data: object) -> ModelOutput:
    """Build a ModelOutput from parsed JSON, keeping an ill-shaped single term as MalformedTerm."""
    if not isinstance(data, dict):
        raise ModelOutputError("the reply is not a JSON object")
    deal_type, raw_terms = data.get("deal_type"), data.get("terms")
    if not isinstance(deal_type, str) or not isinstance(raw_terms, dict):
        raise ModelOutputError("the reply needs a deal_type string and a terms object")
    terms: dict[str, TermOutput | MalformedTerm] = {}
    for key, raw in raw_terms.items():
        try:
            terms[str(key)] = TermOutput.model_validate(raw)
        except ValidationError:
            terms[str(key)] = MalformedTerm(raw=json.dumps(raw, ensure_ascii=False))
    return ModelOutput(deal_type=deal_type, terms=terms)


def parse_model_output(text: str) -> ModelOutput:
    """Parse the model's reply text. Raises ModelOutputError if it is not the expected object."""
    try:
        data = json.loads(text)
    except ValueError:
        raise ModelOutputError("the reply is not valid JSON") from None
    return output_from_object(data)
