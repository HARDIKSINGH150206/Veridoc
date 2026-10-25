"""Demo-only fixture ingestion for FR-IMP-007 and FR-IMP-009."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from packages.ingest.samples import (
    SampleNotFound,
    SampleUnavailable,
    list_samples,
    load_messages,
    load_sample,
)

router = APIRouter(prefix="/ingest", tags=["ingest"])

FIXTURES = Path(__file__).resolve().parents[3] / "packages/ingest/fixtures"


def _require_demo(request: Request) -> None:
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")


@router.get("/samples")
def samples(request: Request) -> JSONResponse:
    """Names of the bundled demo samples (demo mode only)."""
    # STUB: replaced by #29 (shared walking-skeleton integration).
    _require_demo(request)
    return JSONResponse({"samples": list_samples(FIXTURES)})


@router.get("/samples/{sample_id}")
def sample(sample_id: str, request: Request) -> JSONResponse:
    """A bundled sample with its participants, playbook and messages (demo mode only)."""
    # STUB: replaced by #29 (shared walking-skeleton integration).
    _require_demo(request)
    try:
        loaded = load_sample(sample_id, FIXTURES)
    except SampleNotFound:
        raise HTTPException(status_code=404, detail="Not found") from None
    except SampleUnavailable:
        raise HTTPException(status_code=503, detail="Sample data unavailable") from None
    return JSONResponse(
        {
            "playbook_id": loaded.playbook_id,
            "participants": [p.model_dump(mode="json") for p in loaded.participants],
            "messages": [m.model_dump(mode="json") for m in loaded.messages],
        }
    )


@router.get("/samples/{sample_id}/messages")
def sample_messages(sample_id: str, request: Request) -> JSONResponse:
    """Return contract-validated synthetic messages only when demo mode is enabled."""
    # STUB: replaced by #29 (shared walking-skeleton integration).
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    directory = FIXTURES / "messages"
    try:
        messages = load_messages(sample_id, directory)
    except SampleNotFound:
        raise HTTPException(status_code=404, detail="Not found") from None
    except SampleUnavailable:
        raise HTTPException(status_code=503, detail="Sample data unavailable") from None
    return JSONResponse([message.model_dump(mode="json") for message in messages])
