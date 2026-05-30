"""OpenRouter embedding service with batching + retry."""
from __future__ import annotations

import asyncio
from collections.abc import Iterable

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.integrations.openrouter_client import create_embeddings

logger = get_logger("embedding")


class EmbeddingService:
    """Wraps OpenRouter embeddings with batching."""

    BATCH_SIZE = 100

    def __init__(self) -> None:
        self.model = settings.OPENROUTER_EMBEDDING_MODEL
        self.dim = settings.EMBEDDING_DIM

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            result = await asyncio.wait_for(
                create_embeddings(texts),
                timeout=settings.OPENROUTER_EMBEDDING_TIMEOUT_SECONDS,
            )
        except TimeoutError as e:
            logger.error("embedding_timeout", batch_size=len(texts))
            raise ExternalServiceError("OpenRouter embedding timed out") from e
        except ExternalServiceError:
            raise
        except Exception as e:
            logger.error("embedding_failed", error=str(e), batch_size=len(texts))
            raise ExternalServiceError(f"OpenRouter embedding failed: {e}") from e
        return result

    async def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        """Embed a list/iterable of texts, batching to respect API limits."""
        texts = [t.strip() for t in texts if t and t.strip()]
        if not texts:
            return []
        out: list[list[float]] = []
        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i : i + self.BATCH_SIZE]
            vectors = await self._embed_batch(batch)
            out.extend(vectors)
        logger.info("embedded", count=len(out))
        return out

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query text for retrieval."""
        try:
            result = await asyncio.wait_for(
                create_embeddings([text]),
                timeout=settings.OPENROUTER_EMBEDDING_TIMEOUT_SECONDS,
            )
        except TimeoutError as e:
            logger.error("embedding_query_timeout")
            raise ExternalServiceError("OpenRouter embedding timed out") from e
        except ExternalServiceError:
            raise
        except Exception as e:
            logger.error("embedding_query_failed", error=str(e))
            raise ExternalServiceError(f"OpenRouter embedding failed: {e}") from e
        return result[0]


embedding_service = EmbeddingService()
