"""Repository validation, cloning, and cleanup."""

import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from git import GitCommandError, Repo

from app.core.config import Settings
from app.core.exceptions import AnalysisError, InvalidRepositoryUrlError


class RepositoryService:
    """Handles the short-lived local clone used for one analysis job."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate and normalize a public GitHub repository URL."""

        parsed = urlparse(url.strip())
        parts = [part for part in parsed.path.split("/") if part]

        if (
            parsed.scheme != "https"
            or parsed.netloc.lower() != "github.com"
            or len(parts) != 2
        ):
            raise InvalidRepositoryUrlError(
                "Enter a public repository URL in the form "
                "https://github.com/owner/repository."
            )

        owner, repository = parts
        repository = repository.removesuffix(".git")
        if not owner or not repository:
            raise InvalidRepositoryUrlError(
                "The GitHub owner and repository are required."
            )

        return f"https://github.com/{owner}/{repository}.git"

    @contextmanager
    def cloned_repository(self, url: str) -> Generator[Path, None, None]:
        """Yield a full temporary clone and always delete it afterward."""

        clone_url = self.validate_url(url)
        clone_dir = Path(tempfile.mkdtemp(prefix="cea-analysis-"))

        try:
            try:
                Repo.clone_from(clone_url, clone_dir)
            except GitCommandError as exc:
                raise AnalysisError(
                    "Unable to clone this repository. Confirm that it is public "
                    "and reachable."
                ) from exc

            yield clone_dir
        finally:
            shutil.rmtree(clone_dir, ignore_errors=True)
