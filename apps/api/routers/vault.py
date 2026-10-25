"""Vault routes (Area 3). Thin: call packages/vault and return contract models."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse

from packages.vault.fake_receipt import FakeReceiptUnavailable, fake_receipt

router = APIRouter(prefix="/vault", tags=["vault"])

DealId = Annotated[str, Path(pattern=r"^[A-Za-z0-9_-]{1,64}$")]


@router.get("/deals/{deal_id}/receipt")
def receipt(deal_id: DealId, request: Request) -> JSONResponse:
    """Demo mode only: a clearly labelled fake receipt for the walking skeleton (FR-VLT-002)."""
    # STUB: replaced by #31 (walking-skeleton integration); the real receipt follows in Phase 3.
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        made = fake_receipt(deal_id)
    except FakeReceiptUnavailable:
        raise HTTPException(status_code=503, detail="Receipt unavailable") from None
    return JSONResponse(made.model_dump(mode="json"))
