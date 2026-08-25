import pytest

from app.core.config import Settings
from app.core.exceptions import InvalidRepositoryUrlError
from app.services.repository import RepositoryService


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://github.com/openai/openai-python",
            "https://github.com/openai/openai-python.git",
        ),
        (
            "https://github.com/openai/openai-python.git",
            "https://github.com/openai/openai-python.git",
        ),
    ],
)
def test_validate_url_accepts_public_repository_urls(url: str, expected: str) -> None:
    assert RepositoryService(Settings()).validate_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/openai/openai-python",
        "https://gitlab.com/openai/openai-python",
        "https://github.com/openai",
        "https://github.com/openai/openai-python/issues",
    ],
)
def test_validate_url_rejects_non_repository_urls(url: str) -> None:
    with pytest.raises(InvalidRepositoryUrlError):
        RepositoryService(Settings()).validate_url(url)
