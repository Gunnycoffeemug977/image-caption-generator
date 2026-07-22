"""FastAPI application entry point.

Run locally with:

    uvicorn main:app --reload

or simply:

    python main.py
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config import get_settings
from dependencies import get_repository, get_vision_client
from exceptions import AppError
from logging_config import configure_logging
from routes import api_router, pages_router

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up singletons and log startup diagnostics."""
    get_repository()
    get_vision_client()
    if settings.is_configured:
        logger.info("Startup complete. Using model '%s'.", settings.openai_model)
    else:
        logger.warning(
            "OPENAI_API_KEY is not set. The API will reject caption requests "
            "until it is configured in the .env file."
        )
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.app_name,
    description="Enterprise-grade AI image captioning service powered by OpenAI vision models.",
    version=settings.app_version,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages_router)
app.include_router(api_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Translate domain exceptions into a consistent JSON error envelope."""
    logger.warning("Handled error on %s %s: %s", request.method, request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message, "detail": None})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development",
    )
