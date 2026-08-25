"""HTTP request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from app.models import EvolutionReport
from app.services.analysis_jobs import AnalysisJob, JobStatus


class CreateAnalysisRequest(BaseModel):
    """Payload accepted when a user starts an analysis."""

    repository_url: HttpUrl
    snapshot_count: int = Field(default=15, ge=1, le=60)


class AnalysisJobResponse(BaseModel):
    """Public representation of one analysis job."""

    id: str
    repository_url: str
    snapshot_count: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    report: EvolutionReport | None = None
    error: str | None = None

    @classmethod
    def from_job(cls, job: AnalysisJob) -> "AnalysisJobResponse":
        return cls(
            id=job.id,
            repository_url=job.repository_url,
            snapshot_count=job.snapshot_count,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            report=job.report,
            error=job.error,
        )
