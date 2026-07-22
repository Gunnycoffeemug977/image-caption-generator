"""SQLite persistence layer for caption history.

This module is the infrastructure-layer implementation of caption
storage (Clean Architecture). It exposes a small async repository API so
the service layer never has to know it is backed by SQLite. Synchronous
sqlite3 calls are pushed to a worker thread via `asyncio.to_thread` so the
FastAPI event loop is never blocked.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS captions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    mode TEXT NOT NULL,
    tone TEXT NOT NULL,
    caption TEXT NOT NULL,
    detailed_description TEXT,
    alt_text TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    mood TEXT,
    model TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class CaptionRepository:
    """Repository responsible for persisting and retrieving caption history."""

    def __init__(self, database_path: str) -> None:
        self._path = Path(database_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # -- synchronous internals (run in a worker thread) ----------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_SCHEMA)
            conn.commit()
        logger.info("Database ready at %s", self._path)

    def _insert(self, record: dict[str, Any]) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO captions
                    (filename, mode, tone, caption, detailed_description,
                     alt_text, tags, mood, model, created_at)
                VALUES
                    (:filename, :mode, :tone, :caption, :detailed_description,
                     :alt_text, :tags, :mood, :model, :created_at)
                """,
                record,
            )
            conn.commit()
            return int(cursor.lastrowid)

    def _fetch_all(self, limit: int, offset: int) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM captions ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]

    def _count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM captions").fetchone()
            return int(row["c"])

    def _fetch_one(self, item_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM captions WHERE id = ?", (item_id,)).fetchone()
            return dict(row) if row else None

    def _delete(self, item_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM captions WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0

    # -- async public API -----------------------------------------------------

    async def save(
        self,
        *,
        filename: str,
        mode: str,
        tone: str,
        caption: str,
        detailed_description: str | None,
        alt_text: str,
        tags: list[str],
        mood: str | None,
        model: str,
    ) -> dict[str, Any]:
        """Persist a generated caption and return the stored record."""
        record = {
            "filename": filename,
            "mode": mode,
            "tone": tone,
            "caption": caption,
            "detailed_description": detailed_description,
            "alt_text": alt_text,
            "tags": json.dumps(tags),
            "mood": mood,
            "model": model,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        new_id = await asyncio.to_thread(self._insert, record)
        saved = await asyncio.to_thread(self._fetch_one, new_id)
        assert saved is not None
        return self._deserialize(saved)

    async def list_history(self, limit: int = 50, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        """Return a page of history rows (most recent first) and the total count."""
        rows = await asyncio.to_thread(self._fetch_all, limit, offset)
        total = await asyncio.to_thread(self._count)
        return [self._deserialize(r) for r in rows], total

    async def get(self, item_id: int) -> dict[str, Any] | None:
        """Return a single history row by id, or None if it does not exist."""
        row = await asyncio.to_thread(self._fetch_one, item_id)
        return self._deserialize(row) if row else None

    async def delete(self, item_id: int) -> bool:
        """Delete a history row by id. Returns True if a row was removed."""
        return await asyncio.to_thread(self._delete, item_id)

    @staticmethod
    def _deserialize(row: dict[str, Any]) -> dict[str, Any]:
        row = dict(row)
        row["tags"] = json.loads(row.get("tags") or "[]")
        return row
