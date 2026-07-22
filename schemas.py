"""Pydantic v2 data schemas shared across the application layers."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CaptionMode(str, Enum):
    """The captioning strategy requested by the client."""

    STANDARD = "standard"
    DETAILED = "detailed"
    ACCESSIBILITY = "accessibility"


class CaptionTone(str, Enum):
    """The writing tone requested for the generated caption."""

    NEUTRAL = "neutral"
    CREATIVE = "creative"
    TECHNICAL = "technical"


class CaptionRequest(BaseModel):
    """Options accompanying an image caption generation request."""

    mode: CaptionMode = CaptionMode.STANDARD
    tone: CaptionTone = CaptionTone.NEUTRAL
    language: str = Field(default="en", min_length=2, max_length=8)


class CaptionResult(BaseModel):
    """The structured result produced by the vision AI service."""

    model_config = ConfigDict(from_attributes=True)

    caption: str
    detailed_description: str | None = None
    alt_text: str
    tags: list[str] = Field(default_factory=list)
    mood: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)


class HistoryItem(BaseModel):
    """A previously generated caption stored in the local database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    mode: str
    tone: str
    caption: str
    detailed_description: str | None = None
    alt_text: str
    tags: list[str]
    mood: str | None = None
    model: str
    created_at: datetime


class HistoryListResponse(BaseModel):
    """A page of caption history results."""

    items: list[HistoryItem]
    total: int


class HealthResponse(BaseModel):
    """Response body for the health check endpoint."""

    status: str
    app_name: str
    version: str
    model: str
    configured: bool


class ErrorResponse(BaseModel):
    """Standard error envelope returned to API clients."""

    error: str
    detail: str | None = None
