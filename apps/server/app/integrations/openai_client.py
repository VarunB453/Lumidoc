"""Google Gemini API client wrapper for centralized configuration.

Note: OpenAI client is retained only for Whisper transcription.
"""
from __future__ import annotations

from functools import lru_cache

import google.generativeai as genai
import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("gemini_client")

_gemini_configured = False


def _ensure_gemini() -> None:
    global _gemini_configured
    if not _gemini_configured:
        if not settings.GOOGLE_API_KEY:
            logger.warning("google_api_key_not_set")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        _gemini_configured = True


@lru_cache(maxsize=1)
def get_openai_client() -> AsyncOpenAI:
    """Return a cached async OpenAI client instance (used for Whisper only)."""
    if not settings.OPENAI_API_KEY:
        logger.warning("openai_api_key_not_set")
    return AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.WHISPER_TIMEOUT_SECONDS,
        http_client=httpx.AsyncClient(
            timeout=settings.WHISPER_TIMEOUT_SECONDS,
            follow_redirects=True,
        ),
    )


async def create_chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Create a chat completion using Google Gemini and return the response text."""
    _ensure_gemini()
    model_name = model or settings.GEMINI_MODEL
    temp = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
    max_tok = max_tokens or settings.GEMINI_MAX_TOKENS

    # Extract system instruction and user messages
    system_parts = [m["content"] for m in messages if m.get("role") == "system"]
    user_parts = [m["content"] for m in messages if m.get("role") != "system"]

    gemini_model = genai.GenerativeModel(
        model_name,
        system_instruction="\n".join(system_parts) if system_parts else None,
    )
    response = gemini_model.generate_content(
        "\n".join(user_parts),
        generation_config=genai.GenerationConfig(
            temperature=temp,
            max_output_tokens=max_tok,
        ),
    )
    return response.text or ""


async def create_embedding(text: str) -> list[float]:
    """Create an embedding vector for the given text using Google Gemini."""
    _ensure_gemini()
    result = genai.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]


async def transcribe_audio(file_path: str, language: str = "en") -> str:
    """Transcribe an audio file using OpenAI Whisper."""
    client = get_openai_client()
    with open(file_path, "rb") as audio_file:
        response = await client.audio.transcriptions.create(
            model=settings.OPENAI_WHISPER_MODEL,
            file=audio_file,
            language=language,
        )
    return response.text
