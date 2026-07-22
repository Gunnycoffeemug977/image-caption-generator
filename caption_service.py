"""Application service layer orchestrating image captioning use cases.

This is the Clean Architecture "use case" layer: it depends only on
abstractions (the vision client and the repository) and contains no
FastAPI- or SQLite-specific code, so it can be tested in isolation.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from database import CaptionRepository
from exceptions import ImageTooLargeError, InvalidImageError
from openai_client import VisionCaptionClient
from schemas import CaptionMode, CaptionResult, CaptionTone, HistoryItem, HistoryListResponse
from utils import human_file_size, sniff_image_mime, to_data_url

logger = logging.getLogger(__name__)


class CaptionService:
    """Coordinates validation, AI vision calls, and history persistence."""

    def __init__(
        self,
        vision_client: VisionCaptionClient,
        repository: CaptionRepository,
        *,
        max_upload_bytes: int,
        allowed_types: list[str],
    ) -> None:
        self._vision_client = vision_client
        self._repository = repository
        self._max_upload_bytes = max_upload_bytes
        self._allowed_types = allowed_types

    def validate_image(self, data: bytes) -> str:
        """Validate raw upload bytes and return the detected MIME type."""
        if len(data) == 0:
            raise InvalidImageError("The uploaded file is empty.")
        if len(data) > self._max_upload_bytes:
            raise ImageTooLargeError(
                f"Image is {human_file_size(len(data))}; the maximum allowed "
                f"size is {human_file_size(self._max_upload_bytes)}."
            )
        mime_type = sniff_image_mime(data)
        if mime_type is None or mime_type not in self._allowed_types:
            raise InvalidImageError("Unsupported image format. Please upload JPEG, PNG, or WEBP.")
        return mime_type

    async def generate_and_store(
        self,
        *,
        filename: str,
        data: bytes,
        mode: CaptionMode,
        tone: CaptionTone,
        language: str,
    ) -> CaptionResult:
        """Validate an image, generate a caption via the vision AI, and store it."""
        mime_type = self.validate_image(data)
        data_url = to_data_url(data, mime_type)

        logger.info(
            "Generating caption for '%s' (%s, mode=%s, tone=%s)",
            filename,
            human_file_size(len(data)),
            mode.value,
            tone.value,
        )

        raw = await self._vision_client.generate_caption(
            image_data_url=data_url, mode=mode, tone=tone, language=language
        )

        result = CaptionResult(
            caption=raw.get("caption", ""),
            detailed_description=raw.get("detailed_description"),
            alt_text=raw.get("alt_text") or raw.get("caption", ""),
            tags=list(raw.get("tags", [])),
            mood=raw.get("mood"),
            confidence=0.92,
        )

        await self._repository.save(
            filename=filename,
            mode=mode.value,
            tone=tone.value,
            caption=result.caption,
            detailed_description=result.detailed_description,
            alt_text=result.alt_text,
            tags=result.tags,
            mood=result.mood,
            model=self._vision_client.model,
        )
        return result

    async def stream_caption(
        self,
        *,
        data: bytes,
        mode: CaptionMode,
        tone: CaptionTone,
        language: str,
    ) -> AsyncIterator[str]:
        """Validate an image and stream a plain-text caption preview."""
        mime_type = self.validate_image(data)
        data_url = to_data_url(data, mime_type)
        async for chunk in self._vision_client.stream_caption(
            image_data_url=data_url, mode=mode, tone=tone, language=language
        ):
            yield chunk

    async def list_history(self, limit: int, offset: int) -> HistoryListResponse:
        """Return a paginated page of caption history."""
        rows, total = await self._repository.list_history(limit=limit, offset=offset)
        items = [HistoryItem.model_validate(row) for row in rows]
        return HistoryListResponse(items=items, total=total)

    async def get_history_item(self, item_id: int) -> HistoryItem | None:
        """Fetch a single history item by id."""
        row = await self._repository.get(item_id)
        return HistoryItem.model_validate(row) if row else None

    async def delete_history_item(self, item_id: int) -> bool:
        """Delete a single history item by id."""
        return await self._repository.delete(item_id)
