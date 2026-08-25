"""In-memory background jobs for repository analysis."""

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from threading import Lock
from uuid import uuid4

from app.analyzer import analyze_repository
from app.core.config import Settings
from app.core.exceptions import AnalysisError
from app.models import EvolutionReport
from app.services.repository import RepositoryService

logger = logging.getLogger(__name__)


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalysisJob:
    """State retained for an in-flight or completed analysis request."""

    id: str
    repository_url: str
    snapshot_count: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    report: EvolutionReport | None = None
    error: str | None = None


class AnalysisJobService:
    """Schedules and tracks analysis work without tying it to HTTP requests."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.repositories = RepositoryService(settings)
        self.executor = ThreadPoolExecutor(
            max_workers=settings.max_workers,
            thread_name_prefix="repository-analysis",
        )
        self.jobs: dict[str, AnalysisJob] = {}
        self.futures: dict[str, Future[None]] = {}
        self.lock = Lock()

    def submit(self, repository_url: str, snapshot_count: int) -> AnalysisJob:
        """Validate input, create a job, and submit it to the executor."""

        normalized_url = self.repositories.validate_url(repository_url)
        now = datetime.now(UTC)
        job = AnalysisJob(
            id=str(uuid4()),
            repository_url=normalized_url.removesuffix(".git"),
            snapshot_count=snapshot_count,
            status=JobStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )

        with self.lock:
            self.jobs[job.id] = job
            self.futures[job.id] = self.executor.submit(self._run, job.id)

        return job

    def get(self, job_id: str) -> AnalysisJob | None:
        """Return a job by id, if it exists."""

        with self.lock:
            return self.jobs.get(job_id)

    def shutdown(self) -> None:
        """Stop accepting work when the web application exits."""

        self.executor.shutdown(wait=False, cancel_futures=True)

    def _run(self, job_id: str) -> None:
        self._update(job_id, status=JobStatus.RUNNING)
        job = self.get(job_id)
        if job is None:
            return

        try:
            with self.repositories.cloned_repository(
                job.repository_url
            ) as repository_path:
                report = analyze_repository(
                    repository_path,
                    snapshot_count=job.snapshot_count,
                    use_llm=True,
                )
            self._update(job_id, status=JobStatus.COMPLETED, report=report)
        except AnalysisError as exc:
            self._update(job_id, status=JobStatus.FAILED, error=str(exc))
        except Exception:
            logger.exception("Analysis job %s failed", job_id)
            self._update(
                job_id,
                status=JobStatus.FAILED,
                error="Analysis failed unexpectedly. Please try another repository.",
            )

    def _update(
        self,
        job_id: str,
        *,
        status: JobStatus,
        report: EvolutionReport | None = None,
        error: str | None = None,
    ) -> None:
        with self.lock:
            job = self.jobs.get(job_id)
            if job is None:
                return
            job.status = status
            job.updated_at = datetime.now(UTC)
            job.report = report
            job.error = error
