"""Centralized logging configuration for the application."""

from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger with a single structured stream handler.

    Safe to call multiple times; subsequent calls are no-ops if handlers
    are already attached, which avoids duplicate log lines under the
    uvicorn --reload development server.
    """
    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Quiet noisy third-party loggers so application logs remain readable.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
