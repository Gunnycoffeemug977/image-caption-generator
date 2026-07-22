"""Application configuration.

Centralizes all environment-driven configuration using Pydantic v2 settings.
Values are read from process environment variables and, when present, a
local `.env` file. This module is the single source of truth for
configuration across the application (Clean Architecture: configuration
lives at the outermost / infrastructure layer and is injected inward).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Strongly-typed application settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- OpenAI / Vision AI -------------------------------------------------
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_timeout_seconds: int = Field(default=60, alias="OPENAI_TIMEOUT_SECONDS")

    # --- Application ----------------------------------------------------------
    app_name: str = Field(default="Image Caption Generator", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # --- Upload limits ----------------------------------------------------
    max_upload_mb: int = Field(default=8, alias="MAX_UPLOAD_MB")
    allowed_image_types: str = Field(
        default="image/jpeg,image/png,image/webp", alias="ALLOWED_IMAGE_TYPES"
    )

    # --- Persistence --------------------------------------------------------
    database_path: str = Field(default="data/history.db", alias="DATABASE_PATH")

    # --- Logging --------------------------------------------------------------
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def allowed_types_list(self) -> list[str]:
        """Return the allowed MIME types as a clean list."""
        return [t.strip() for t in self.allowed_image_types.split(",") if t.strip()]

    @property
    def max_upload_bytes(self) -> int:
        """Return the maximum upload size expressed in bytes."""
        return self.max_upload_mb * 1024 * 1024

    @property
    def is_configured(self) -> bool:
        """Whether an OpenAI API key has been supplied."""
        return bool(self.openai_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    """Return a cached, process-wide Settings instance."""
    return Settings()
