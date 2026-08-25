"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import api, pages
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.analysis_jobs import AnalysisJobService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and release process-wide resources."""

    configure_logging()
    app.state.settings = get_settings()
    app.state.analysis_jobs = AnalysisJobService(app.state.settings)
    yield
    app.state.analysis_jobs.shutdown()


def create_app() -> FastAPI:
    """Build the HTTP application without starting a server."""

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )
    static_directory = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_directory), name="static")
    app.include_router(pages)
    app.include_router(api)
    return app


app = create_app()
