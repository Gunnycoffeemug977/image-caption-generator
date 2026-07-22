"""Small, dependency-free utility helpers.

Image type detection is implemented via raw magic-byte sniffing rather
than the deprecated `imghdr` standard library module (removed in
Python 3.13), keeping the project forward compatible.
"""

from __future__ import annotations

import base64


def sniff_image_mime(data: bytes) -> str | None:
    """Detect an image's MIME type from its magic bytes.

    Returns one of "image/jpeg", "image/png", "image/webp", or None if the
    bytes do not match a recognized, supported image format.
    """
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def to_data_url(data: bytes, mime_type: str) -> str:
    """Encode raw image bytes as a base64 data: URL suitable for the OpenAI API."""
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def human_file_size(num_bytes: int) -> str:
    """Format a byte count as a human-readable string, e.g. '1.4 MB'."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def safe_filename(filename: str | None) -> str:
    """Return a sanitized filename, falling back to a generic name."""
    if not filename:
        return "upload.jpg"
    cleaned = "".join(c for c in filename if c.isalnum() or c in ("-", "_", ".", " ")).strip()
    return cleaned or "upload.jpg"
