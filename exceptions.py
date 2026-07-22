"""Domain-level exceptions.

Using typed exceptions (instead of raising HTTPException deep inside the
service layer) keeps the service and infrastructure layers framework
agnostic, per Clean Architecture. The API layer translates these into
HTTP responses in `main.py`.
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for all handled application errors."""

    def __init__(self, message: str, *, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidImageError(AppError):
    """Raised when an uploaded file is missing, empty, or not a supported image."""

    def __init__(self, message: str = "The uploaded file is not a supported image.") -> None:
        super().__init__(message, status_code=400)


class ImageTooLargeError(AppError):
    """Raised when an uploaded image exceeds the configured size limit."""

    def __init__(self, message: str = "The uploaded image exceeds the maximum allowed size.") -> None:
        super().__init__(message, status_code=413)


class VisionServiceError(AppError):
    """Raised when the OpenAI vision service fails or returns malformed output."""

    def __init__(self, message: str = "The vision AI service failed to process the image.") -> None:
        super().__init__(message, status_code=502)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "The requested resource was not found.") -> None:
        super().__init__(message, status_code=404)


class NotConfiguredError(AppError):
    """Raised when the application is missing required configuration (e.g. API key)."""

    def __init__(self, message: str = "The server is not configured with an OpenAI API key.") -> None:
        super().__init__(message, status_code=503)
