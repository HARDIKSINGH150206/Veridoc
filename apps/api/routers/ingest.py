"""Demo-only fixture ingestion for FR-IMP-007 and FR-IMP-009."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from packages.ingest.samples import SampleNotFound, SampleUnavailable, load_messages

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.get("/samples/{sample_id}/messages")
def sample_messages(sample_id: str, request: Request) -> JSONResponse:
    """Return contract-validated synthetic messages only when demo mode is enabled."""
    # STUB: replaced by #29 (shared walking-skeleton integration).
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    directory = Path(__file__).resolve().parents[3] / "packages/ingest/fixtures/messages"
    try:
        messages = load_messages(sample_id, directory)
    except SampleNotFound:
        raise HTTPException(status_code=404, detail="Not found") from None
    except SampleUnavailable:
        raise HTTPException(status_code=503, detail="Sample data unavailable") from None
    return JSONResponse([message.model_dump(mode="json") for message in messages])
