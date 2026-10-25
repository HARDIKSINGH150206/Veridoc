"""Vault routes (Area 3). Thin: call packages/vault and return contract models."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse

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
