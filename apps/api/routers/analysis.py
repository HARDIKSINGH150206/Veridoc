"""Analysis routes. Owner: Area 2. Thin: call packages/intelligence."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from packages.ingest.samples import SampleNotFound, SampleUnavailable, load_sample
from packages.intelligence.demo_analysis import analyze_demo
from packages.intelligence.model_adapter import UnrecordedChat, build_adapter

router = APIRouter(prefix="/analysis", tags=["analysis"])

ROOT = Path(__file__).resolve().parents[3]
INGEST_FIXTURES = ROOT / "packages/ingest/fixtures"
RECORDINGS = ROOT / "packages/intelligence/fixtures/recordings"


@router.get("/samples/{sample_id}/terms")
def sample_terms(sample_id: str, request: Request) -> JSONResponse:
    """Demo mode only: unconfirmed terms for a bundled sample, from the configured model adapter."""
    # STUB: replaced by #30 (walking-skeleton integration); real analysis streams (SSE) later.
    settings = request.app.state.settings
    if not settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        sample = load_sample(sample_id, INGEST_FIXTURES)
    except SampleNotFound:
        raise HTTPException(status_code=404, detail="Not found") from None
    except SampleUnavailable:
        raise HTTPException(status_code=503, detail="Sample data unavailable") from None
    try:
        adapter = build_adapter(settings.model_mode, RECORDINGS)
        terms = analyze_demo(sample, adapter)
    except NotImplementedError as error:
        raise HTTPException(status_code=501, detail=str(error)) from None
    except (UnrecordedChat, ValueError):
        raise HTTPException(
            status_code=503, detail="No recorded analysis for this sample"
        ) from None
    return JSONResponse({"demo": True, "terms": [t.model_dump(mode="json") for t in terms]})
