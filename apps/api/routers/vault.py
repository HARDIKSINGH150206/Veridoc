"""Vault routes (Area 3). Thin: call packages/vault and return contract models."""

import secrets
from datetime import datetime
from pathlib import Path as FilePath
from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Path, Request
from fastapi.responses import JSONResponse

from packages.contracts import PlaybookRef
from packages.ingest.demo_recap import (
    ConfirmationRequired,
    InvalidConfirmation,
    check_confirmed_terms,
    parse_confirmed_terms,
)
from packages.ingest.samples import SampleNotFound, SampleUnavailable, load_sample
from packages.integrity.hashing import SALT_SIZE
from packages.vault.demo_record import record_demo
from packages.vault.fake_receipt import fake_receipt

router = APIRouter(prefix="/vault", tags=["vault"])

DealId = Annotated[
    str,
    Path(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
]
"""A deal id is a lowercase UUID, as in packages/contracts."""


@router.get("/deals/{deal_id}/receipt")
def receipt(deal_id: DealId, request: Request) -> JSONResponse:
    """Demo mode only: a clearly labelled fake receipt for the walking skeleton (FR-VLT-002)."""
    # STUB: replaced by #31 (walking-skeleton integration); the real receipt follows in Phase 3.
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    return JSONResponse(fake_receipt(deal_id).model_dump(mode="json"))


INGEST_FIXTURES = FilePath(__file__).resolve().parents[3] / "packages/ingest/fixtures"


@router.post("/samples/{sample_id}/record")
def record_sample(
    sample_id: str,
    request: Request,
    body: Any = Body(default=None),  # noqa: B008
) -> JSONResponse:
    """Demo mode only: record a sample's messages and the confirmed terms, return the receipt.

    Only terms the primary user confirmed are accepted; nothing produced by the AI reaches this
    route without that confirmation.
    """
    # STUB: replaced by #31 (walking-skeleton integration); the real vault follows in Phase 3.
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        sample = load_sample(sample_id, INGEST_FIXTURES)
    except SampleNotFound:
        raise HTTPException(status_code=404, detail="Not found") from None
    except SampleUnavailable:
        raise HTTPException(status_code=503, detail="Sample data unavailable") from None
    try:
        terms = parse_confirmed_terms(body)
        check_confirmed_terms(sample, terms)
    except (ConfirmationRequired, InvalidConfirmation) as error:
        raise HTTPException(status_code=422, detail=str(error)) from None
    playbook = PlaybookRef(key=sample.playbook_id, version=1)  # STUB: replaced by #19
    salts = [secrets.token_bytes(SALT_SIZE) for _ in sample.messages]
    recorded_at = datetime.now().astimezone().replace(microsecond=0)
    record = record_demo(list(sample.messages), terms, playbook, salts, recorded_at)
    return JSONResponse(
        {
            "demo": True,
            "version": record.version.model_dump(mode="json"),
            "receipt": record.receipt.model_dump(mode="json"),
            "leaf_rows": [row.model_dump(mode="json") for row in record.leaf_rows],
        }
    )
