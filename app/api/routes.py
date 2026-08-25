"""HTML and JSON routes for the web application."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.schemas import AnalysisJobResponse, CreateAnalysisRequest
from app.core.config import Settings
from app.core.exceptions import InvalidRepositoryUrlError
from app.services.analysis_jobs import AnalysisJobService

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

pages = APIRouter()
api = APIRouter(prefix="/api", tags=["analyses"])


@pages.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Render the architecture-analysis dashboard."""

    settings: Settings = request.app.state.settings
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "default_snapshots": settings.default_snapshots,
            "max_snapshots": settings.max_snapshots,
        },
    )


@api.post(
    "/analyses",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_analysis(
    request: Request,
    payload: CreateAnalysisRequest,
) -> AnalysisJobResponse:
    """Start a non-blocking repository analysis."""

    service: AnalysisJobService = request.app.state.analysis_jobs
    try:
        job = service.submit(str(payload.repository_url), payload.snapshot_count)
    except InvalidRepositoryUrlError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return AnalysisJobResponse.from_job(job)


@api.get("/analyses/{job_id}", response_model=AnalysisJobResponse)
def get_analysis(request: Request, job_id: str) -> AnalysisJobResponse:
    """Get current status or the completed report for an analysis job."""

    service: AnalysisJobService = request.app.state.analysis_jobs
    job = service.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found.",
        )
    return AnalysisJobResponse.from_job(job)
