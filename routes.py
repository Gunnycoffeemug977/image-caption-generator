"""HTTP route handlers.

This is the outermost (interface adapters) layer: it translates HTTP
requests into calls on `CaptionService` and translates domain exceptions
into HTTP responses. No business logic lives here.
"""

from __future__ import annotations

import io
import logging

from fastapi import APIRouter, Depends, Query, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from caption_service import CaptionService
from config import Settings, get_settings
from dependencies import get_caption_service
from exceptions import NotConfiguredError, NotFoundError
from schemas import (
    CaptionMode,
    CaptionResult,
    CaptionTone,
    HealthResponse,
    HistoryItem,
    HistoryListResponse,
)

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

pages_router = APIRouter(tags=["pages"])
api_router = APIRouter(prefix="/api", tags=["api"])


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@pages_router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Serve the single-page application shell."""
    return templates.TemplateResponse(request, "index.html", {})


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@api_router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Report application health and configuration status."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        model=settings.openai_model,
        configured=settings.is_configured,
    )


# ---------------------------------------------------------------------------
# Captioning
# ---------------------------------------------------------------------------


async def _read_upload(file: UploadFile) -> bytes:
    data = await file.read()
    await file.close()
    return data


@api_router.post("/caption", response_model=CaptionResult)
async def create_caption(
    file: UploadFile,
    mode: CaptionMode = CaptionMode.STANDARD,
    tone: CaptionTone = CaptionTone.NEUTRAL,
    language: str = "en",
    settings: Settings = Depends(get_settings),
    service: CaptionService = Depends(get_caption_service),
) -> CaptionResult:
    """Generate a structured caption for an uploaded image."""
    if not settings.is_configured:
        raise NotConfiguredError()

    data = await _read_upload(file)
    filename = file.filename or "upload.jpg"
    return await service.generate_and_store(
        filename=filename, data=data, mode=mode, tone=tone, language=language
    )


@api_router.post("/caption/stream")
async def stream_caption(
    file: UploadFile,
    mode: CaptionMode = CaptionMode.STANDARD,
    tone: CaptionTone = CaptionTone.NEUTRAL,
    language: str = "en",
    settings: Settings = Depends(get_settings),
    service: CaptionService = Depends(get_caption_service),
) -> StreamingResponse:
    """Stream a plain-text caption preview as Server-Sent Events."""
    if not settings.is_configured:
        raise NotConfiguredError()

    data = await _read_upload(file)

    async def event_stream():
        try:
            async for chunk in service.stream_caption(data=data, mode=mode, tone=tone, language=language):
                safe_chunk = chunk.replace("\r", "").replace("\n", "\\n")
                yield f"data: {safe_chunk}\n\n"
            yield "event: done\ndata: end\n\n"
        except Exception as exc:  # noqa: BLE001 - convert any failure into an SSE error event
            logger.exception("Streaming caption generation failed")
            yield f"event: error\ndata: {exc}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


@api_router.get("/history", response_model=HistoryListResponse)
async def list_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: CaptionService = Depends(get_caption_service),
) -> HistoryListResponse:
    """Return a paginated list of previously generated captions."""
    return await service.list_history(limit=limit, offset=offset)


@api_router.get("/history/{item_id}", response_model=HistoryItem)
async def get_history_item(item_id: int, service: CaptionService = Depends(get_caption_service)) -> HistoryItem:
    """Return a single caption history record."""
    item = await service.get_history_item(item_id)
    if item is None:
        raise NotFoundError(f"History item {item_id} was not found.")
    return item


@api_router.delete("/history/{item_id}", status_code=204, response_model=None)
async def delete_history_item(item_id: int, service: CaptionService = Depends(get_caption_service)) -> Response:
    """Delete a single caption history record."""
    deleted = await service.delete_history_item(item_id)
    if not deleted:
        raise NotFoundError(f"History item {item_id} was not found.")
    return Response(status_code=204)


@api_router.get("/history/{item_id}/download")
async def download_history_item(item_id: int, service: CaptionService = Depends(get_caption_service)) -> StreamingResponse:
    """Download a caption history record as a plain-text file."""
    item = await service.get_history_item(item_id)
    if item is None:
        raise NotFoundError(f"History item {item_id} was not found.")

    lines = [
        f"File: {item.filename}",
        f"Mode: {item.mode}",
        f"Tone: {item.tone}",
        f"Generated: {item.created_at.isoformat()}",
        f"Model: {item.model}",
        "",
        "Caption:",
        item.caption,
    ]
    if item.detailed_description:
        lines += ["", "Detailed description:", item.detailed_description]
    lines += ["", "Alt text:", item.alt_text]
    if item.tags:
        lines += ["", "Tags: " + ", ".join(item.tags)]
    if item.mood:
        lines += ["", f"Mood: {item.mood}"]

    buffer = io.BytesIO("\n".join(lines).encode("utf-8"))
    headers = {"Content-Disposition": f'attachment; filename="caption_{item_id}.txt"'}
    return StreamingResponse(buffer, media_type="text/plain", headers=headers)
