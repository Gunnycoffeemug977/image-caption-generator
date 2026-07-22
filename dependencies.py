"""FastAPI dependency-injection wiring.

Builds singleton infrastructure objects (repository, vision client) once
per process and exposes them to route handlers via `Depends`. This is the
"composition root" that wires Clean Architecture layers together.
"""

from __future__ import annotations

from functools import lru_cache

from caption_service import CaptionService
from config import Settings, get_settings
from database import CaptionRepository
from openai_client import VisionCaptionClient


@lru_cache
def get_repository() -> CaptionRepository:
    """Return a process-wide singleton caption repository."""
    settings = get_settings()
    return CaptionRepository(settings.database_path)


@lru_cache
def get_vision_client() -> VisionCaptionClient:
    """Return a process-wide singleton OpenAI vision client."""
    settings = get_settings()
    return VisionCaptionClient(settings)


@lru_cache
def get_caption_service() -> CaptionService:
    """Return a process-wide singleton caption application service."""
    settings: Settings = get_settings()
    return CaptionService(
        vision_client=get_vision_client(),
        repository=get_repository(),
        max_upload_bytes=settings.max_upload_bytes,
        allowed_types=settings.allowed_types_list,
    )
