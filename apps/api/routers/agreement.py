"""Recap and Blind Handshake routes. Owner: Area 1. Thin: call packages/ingest."""

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import JSONResponse

from packages.ingest.demo_recap import (
    ConfirmationRequired,
    InvalidConfirmation,
    build_demo_recap,
    check_confirmed_terms,
    parse_confirmed_terms,
)
from packages.ingest.samples import SampleNotFound, SampleUnavailable, load_sample

router = APIRouter(prefix="/agreement", tags=["agreement"])

FIXTURES = Path(__file__).resolve().parents[3] / "packages/ingest/fixtures"
FIRST_VERSION = 1


@router.post("/samples/{sample_id}/recap")
def sample_recap(
    sample_id: str,
    request: Request,
    body: Any = Body(default=None),  # noqa: B008
) -> JSONResponse:
    """Demo mode only: the recap with its echo code for the confirmed terms of a sample."""
    # STUB: replaced by #29 (shared walking-skeleton integration).
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        sample = load_sample(sample_id, FIXTURES)
    except SampleNotFound:
        raise HTTPException(status_code=404, detail="Not found") from None
    except SampleUnavailable:
        raise HTTPException(status_code=503, detail="Sample data unavailable") from None
    try:
        terms = parse_confirmed_terms(body)
        check_confirmed_terms(sample, terms)
    except (ConfirmationRequired, InvalidConfirmation) as error:
        raise HTTPException(status_code=422, detail=str(error)) from None
    created_at = datetime.now().astimezone().replace(microsecond=0)
    recap = build_demo_recap(sample.messages[0].deal_id, FIRST_VERSION, terms, created_at)
    return JSONResponse(recap.model_dump(mode="json"))
