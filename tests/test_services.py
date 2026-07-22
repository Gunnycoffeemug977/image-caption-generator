"""Unit tests for the service and utility layers (no FastAPI, no network)."""

from __future__ import annotations

import asyncio

import pytest

from caption_service import CaptionService
from database import CaptionRepository
from exceptions import ImageTooLargeError, InvalidImageError
from utils import human_file_size, safe_filename, sniff_image_mime, to_data_url


def test_sniff_image_mime_detects_png(tiny_png_bytes: bytes):
    assert sniff_image_mime(tiny_png_bytes) == "image/png"


def test_sniff_image_mime_detects_jpeg():
    jpeg_header = b"\xff\xd8\xff\xe0" + b"\x00" * 20
    assert sniff_image_mime(jpeg_header) == "image/jpeg"


def test_sniff_image_mime_rejects_unknown_bytes():
    assert sniff_image_mime(b"not an image at all") is None


def test_to_data_url_has_correct_prefix(tiny_png_bytes: bytes):
    url = to_data_url(tiny_png_bytes, "image/png")
    assert url.startswith("data:image/png;base64,")


def test_human_file_size_formats_kilobytes():
    assert human_file_size(2048) == "2.0 KB"


def test_safe_filename_strips_unsafe_characters():
    assert safe_filename("../../evil<name>.jpg") == "....evilname.jpg"
    assert safe_filename(None) == "upload.jpg"


class _StubVisionClient:
    model = "gpt-4o-mini"


def _build_service(tmp_path) -> CaptionService:
    repo = CaptionRepository(str(tmp_path / "history.db"))
    return CaptionService(
        vision_client=_StubVisionClient(),
        repository=repo,
        max_upload_bytes=1024,
        allowed_types=["image/jpeg", "image/png", "image/webp"],
    )


def test_validate_image_rejects_empty_bytes(tmp_path):
    service = _build_service(tmp_path)
    with pytest.raises(InvalidImageError):
        service.validate_image(b"")


def test_validate_image_rejects_oversized_upload(tmp_path, tiny_png_bytes: bytes):
    service = _build_service(tmp_path)
    oversized = tiny_png_bytes + (b"\x00" * 2000)
    with pytest.raises(ImageTooLargeError):
        service.validate_image(oversized)


def test_validate_image_accepts_valid_png(tmp_path, tiny_png_bytes: bytes):
    service = _build_service(tmp_path)
    assert service.validate_image(tiny_png_bytes) == "image/png"


def test_repository_save_and_list_roundtrip(tmp_path):
    repo = CaptionRepository(str(tmp_path / "history.db"))

    async def _run():
        saved = await repo.save(
            filename="cat.jpg",
            mode="standard",
            tone="neutral",
            caption="A cat sitting on a windowsill.",
            detailed_description=None,
            alt_text="A cat sitting on a windowsill.",
            tags=["cat", "window"],
            mood="peaceful",
            model="gpt-4o-mini",
        )
        assert saved["id"] > 0
        items, total = await repo.list_history(limit=10, offset=0)
        assert total == 1
        assert items[0]["caption"] == "A cat sitting on a windowsill."
        assert items[0]["tags"] == ["cat", "window"]

    asyncio.run(_run())
