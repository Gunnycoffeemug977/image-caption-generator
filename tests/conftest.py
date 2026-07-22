"""Shared pytest fixtures.

Sets required environment variables before the application config is
imported, and provides a FastAPI TestClient with the caption service
dependency overridden by an in-memory fake (no real OpenAI calls are made
during the test suite).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Ensure the project root is importable when tests are run from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-for-unit-tests")
os.environ.setdefault("DATABASE_PATH", "data/test_history.db")


@pytest.fixture
def tiny_png_bytes() -> bytes:
    """A minimal valid 1x1 PNG image, used to exercise upload validation."""
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000"
        "001f15c4890000000d49444154789c63f8cfc0f01f00050001ff8999"
        "3d1d0000000049454e44ae426082"
    )
