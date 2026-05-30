"""OpenRouter client helpers using the OpenAI-compatible API."""
from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger("openrouter")


@lru_cache(maxsize=1)
def get_openrouter_client() -> AsyncOpenAI:
    """Return a cached async OpenRouter client."""
    if not settings.OPENROUTER_API_KEY:
        logger.error("openrouter_api_key_not_set")
        raise ExternalServiceError("OPENROUTER_API_KEY is not configured.")
    return AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
        http_client=httpx.AsyncClient(
            base_url=settings.OPENROUTER_BASE_URL,
            timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
            follow_redirects=True,
        ),
        default_headers={
            "HTTP-Referer": settings.OPENROUTER_SITE_URL,
            "X-Title": settings.OPENROUTER_APP_NAME,
        },
    )


async def create_chat_completion(messages: list[dict[str, str]]) -> str:
    """Create a non-streaming chat completion."""
    try:
        resp = await get_openrouter_client().chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=messages,
            temperature=settings.OPENROUTER_TEMPERATURE,
            max_tokens=settings.OPENROUTER_MAX_TOKENS,
            timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
        )
        return resp.choices[0].message.content or ""
    except ExternalServiceError:
        raise
    except Exception as e:
        logger.error("openrouter_chat_failed", error=str(e))
        raise ExternalServiceError(f"OpenRouter chat failed: {e}") from e


async def stream_chat_completion(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    """Stream chat completion text chunks."""
    try:
        stream = await get_openrouter_client().chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=messages,
            temperature=settings.OPENROUTER_TEMPERATURE,
            max_tokens=settings.OPENROUTER_MAX_TOKENS,
            stream=True,
            timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
        )
        async for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token
    except ExternalServiceError:
        raise
    except Exception as e:
        logger.error("openrouter_stream_failed", error=str(e))
        raise ExternalServiceError(f"OpenRouter stream failed: {e}") from e


async def create_embeddings(texts: list[str]) -> list[list[float]]:
    """Create embeddings for one or more texts."""
    try:
        resp = await get_openrouter_client().embeddings.create(
            model=settings.OPENROUTER_EMBEDDING_MODEL,
            input=texts,
            timeout=settings.OPENROUTER_EMBEDDING_TIMEOUT_SECONDS,
        )
        return [item.embedding for item in resp.data]
    except ExternalServiceError:
        raise
    except Exception as e:
        logger.error("openrouter_embedding_failed", error=str(e), count=len(texts))
        raise ExternalServiceError(f"OpenRouter embedding failed: {e}") from e
