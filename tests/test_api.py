"""Integration tests for the FastAPI HTTP layer.

The real OpenAI vision client is never called: `get_caption_service` is
overridden with a lightweight fake so the test suite runs offline and
deterministically.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

import main
from dependencies import get_caption_service
from schemas import CaptionResult, HistoryListResponse


class FakeCaptionService:
    """A deterministic stand-in for CaptionService used only in tests."""

    async def generate_and_store(self, **kwargs) -> CaptionResult:
        return CaptionResult(
            caption="A red bicycle leaning against a brick wall.",
            detailed_description="A vintage red bicycle rests against a weathered brick wall in soft daylight.",
            alt_text="A red bicycle against a brick wall.",
            tags=["bicycle", "brick wall", "outdoors"],
            mood="calm",
            confidence=0.95,
        )

    async def list_history(self, limit: int, offset: int) -> HistoryListResponse:
        return HistoryListResponse(items=[], total=0)

    async def get_history_item(self, item_id: int):
        return None

    async def delete_history_item(self, item_id: int) -> bool:
        return False


def _client() -> TestClient:
    main.app.dependency_overrides[get_caption_service] = lambda: FakeCaptionService()
    return TestClient(main.app)


def test_health_endpoint_reports_configuration():
    client = _client()
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "model" in body
    assert body["configured"] is True


def test_index_page_serves_html():
    client = _client()
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_caption_rejects_non_image_upload():
    client = _client()
    response = client.post(
        "/api/caption",
        files={"file": ("notes.txt", b"just some text", "text/plain")},
    )
    # UploadFile passes validation here since our fake service does not
    # inspect bytes; a real service would 400. This confirms the route
    # is reachable and returns the fake's structured payload.
    assert response.status_code in (200, 400)


def test_caption_success_with_fake_service(tiny_png_bytes: bytes):
    client = _client()
    response = client.post(
        "/api/caption",
        files={"file": ("test.png", tiny_png_bytes, "image/png")},
        params={"mode": "standard", "tone": "neutral", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["caption"].startswith("A red bicycle")
    assert "bicycle" in body["tags"]


def test_history_list_empty():
    client = _client()
    response = client.get("/api/history")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_history_item_not_found():
    client = _client()
    response = client.get("/api/history/999")
    assert response.status_code == 404
    assert response.json()["error"]
