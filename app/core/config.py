"""Application configuration loaded from the environment."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings with safe defaults for a local deployment."""

    app_name: str = "Architecture Evolution Analyzer"
    environment: str = "development"
    max_snapshots: int = Field(default=60, ge=1, le=100)
    default_snapshots: int = Field(default=15, ge=1, le=100)
    max_workers: int = Field(default=2, ge=1, le=8)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CEA_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()
