"""Application settings, loaded from environment / .env.

Single source of truth for configuration. Never hardcode secrets elsewhere;
read them from here.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    env: str = "local"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    project_name: str = "MenuOS"

    # Database. DATABASE_URL wins if provided; otherwise assembled from parts.
    database_url: str | None = None
    postgres_user: str = "menuos"
    postgres_password: str = "menuos"
    postgres_db: str = "menuos"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Test database (used only by the test suite).
    test_database_url: str | None = None

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so settings are parsed once per process."""
    return Settings()
