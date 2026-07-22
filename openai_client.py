"""Thin wrapper around the OpenAI Responses API for vision-based captioning.

This module isolates all direct OpenAI SDK usage (infrastructure layer),
so the rest of the application depends only on the small, typed interface
exposed here. It uses the Responses API with:

  * `input_image` content parts for image understanding
  * `text.format` (json_schema, strict mode) for structured output
  * `responses.stream(...)` for token-by-token streaming previews
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI

from config import Settings
from exceptions import VisionServiceError
from schemas import CaptionMode, CaptionTone

logger = logging.getLogger(__name__)

# JSON Schema describing the structured caption payload we ask the model
# to return. Strict mode guarantees the model output matches this shape.
CAPTION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "caption": {
            "type": "string",
            "description": "A concise, one to two sentence caption of the image.",
        },
        "detailed_description": {
            "type": "string",
            "description": (
                "A thorough, multi-sentence description covering subjects, "
                "setting, composition, colors, and notable details."
            ),
        },
        "alt_text": {
            "type": "string",
            "description": (
                "A screen-reader-friendly alt text description: concise, "
                "objective, and suitable for accessibility use."
            ),
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Three to eight short keyword tags describing the image contents.",
        },
        "mood": {
            "type": "string",
            "description": "The overall mood or atmosphere conveyed by the image.",
        },
    },
    "required": ["caption", "detailed_description", "alt_text", "tags", "mood"],
    "additionalProperties": False,
}

_MODE_INSTRUCTIONS: dict[CaptionMode, str] = {
    CaptionMode.STANDARD: "Provide a natural, everyday caption a person would use to describe this image.",
    CaptionMode.DETAILED: (
        "Provide an in-depth, richly detailed description covering composition, "
        "lighting, subjects, setting, and context."
    ),
    CaptionMode.ACCESSIBILITY: (
        "Prioritize an objective, accessibility-first description suitable for a "
        "screen reader user who cannot see the image."
    ),
}

_TONE_INSTRUCTIONS: dict[CaptionTone, str] = {
    CaptionTone.NEUTRAL: "Use a clear, neutral, factual tone.",
    CaptionTone.CREATIVE: "Use an evocative, creative, and engaging tone.",
    CaptionTone.TECHNICAL: "Use a precise, technical, analytical tone, as if annotating a computer vision dataset.",
}


class VisionCaptionClient:
    """Encapsulates all calls to the OpenAI Responses API for image captioning."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds,
        )

    @property
    def model(self) -> str:
        """The configured vision model name."""
        return self._settings.openai_model

    def _build_instructions(self, mode: CaptionMode, tone: CaptionTone, language: str) -> str:
        return (
            "You are a professional image captioning assistant for an enterprise "
            "accessibility and content platform. Analyze the supplied image carefully "
            "and respond only with the requested structured fields. "
            f"{_MODE_INSTRUCTIONS[mode]} {_TONE_INSTRUCTIONS[tone]} "
            f"Respond in the language with ISO code '{language}'. "
            "Never invent details that are not visibly present in the image."
        )

    async def generate_caption(
        self,
        *,
        image_data_url: str,
        mode: CaptionMode,
        tone: CaptionTone,
        language: str,
    ) -> dict[str, Any]:
        """Call the Responses API once and return the parsed structured caption."""
        instructions = self._build_instructions(mode, tone, language)
        try:
            response = await self._client.responses.create(
                model=self._settings.openai_model,
                instructions=instructions,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Analyze this image and generate the structured caption fields.",
                            },
                            {"type": "input_image", "image_url": image_data_url},
                        ],
                    }
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "image_caption",
                        "schema": CAPTION_JSON_SCHEMA,
                        "strict": True,
                    }
                },
            )
        except APITimeoutError as exc:
            logger.exception("OpenAI request timed out")
            raise VisionServiceError("The vision service timed out. Please try again.") from exc
        except APIConnectionError as exc:
            logger.exception("Could not connect to OpenAI")
            raise VisionServiceError("Could not connect to the vision service.") from exc
        except APIError as exc:
            logger.exception("OpenAI API returned an error")
            raise VisionServiceError(f"The vision service returned an error: {exc.message}") from exc

        return self._parse_structured_output(response)

    async def stream_caption(
        self,
        *,
        image_data_url: str,
        mode: CaptionMode,
        tone: CaptionTone,
        language: str,
    ) -> AsyncIterator[str]:
        """Yield incremental plain-text caption fragments as they are generated."""
        instructions = self._build_instructions(mode, tone, language) + (
            " Respond with plain descriptive prose only (no JSON, no markdown "
            "formatting) for this live streaming preview."
        )
        try:
            async with self._client.responses.stream(
                model=self._settings.openai_model,
                instructions=instructions,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Describe this image as you generate the caption.",
                            },
                            {"type": "input_image", "image_url": image_data_url},
                        ],
                    }
                ],
            ) as stream:
                async for event in stream:
                    if event.type == "response.output_text.delta":
                        yield event.delta
                await stream.get_final_response()
        except APITimeoutError as exc:
            logger.exception("OpenAI streaming request timed out")
            raise VisionServiceError("The vision service timed out. Please try again.") from exc
        except APIConnectionError as exc:
            logger.exception("Could not connect to OpenAI while streaming")
            raise VisionServiceError("Could not connect to the vision service.") from exc
        except APIError as exc:
            logger.exception("OpenAI streaming API returned an error")
            raise VisionServiceError(f"The vision service streaming failed: {exc.message}") from exc

    @staticmethod
    def _parse_structured_output(response: Any) -> dict[str, Any]:
        text_value = getattr(response, "output_text", None)
        if not text_value:
            raise VisionServiceError("The vision service returned an empty response.")
        try:
            data: dict[str, Any] = json.loads(text_value)
        except json.JSONDecodeError as exc:
            raise VisionServiceError("The vision service returned an unparseable response.") from exc
        return data
