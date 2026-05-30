"""Summary service: OpenRouter summarization + Redis cache."""
from __future__ import annotations

import asyncio
from typing import Any

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.redis_client import cache_get_json, cache_set_json
from app.integrations.openrouter_client import create_chat_completion
from app.models.file import FileModel
from app.models.summary import SummaryModel
from app.services.vector_store import vector_store

logger = get_logger("summary")

SUMMARY_TTL = 86400  # 24h
CACHE_KEY = "summary:{file_id}"


class SummaryService:
    """Summarize a file's chunked text."""

    async def get_or_generate(self, file_id: str, user_id: str) -> dict[str, Any]:
        cache_key = CACHE_KEY.format(file_id=file_id)
        cached = await cache_get_json(cache_key)
        if cached:
            logger.info("summary_cache_hit", file_id=file_id)
            return cached

        existing = await SummaryModel.find_by_file(file_id)
        if existing and existing.get("status") == "ready":
            public = SummaryModel.to_public(existing)
            await cache_set_json(cache_key, public, ttl=SUMMARY_TTL)
            return public

        return await self.generate(file_id, user_id)

    async def generate(self, file_id: str, user_id: str) -> dict[str, Any]:
        file_doc = await FileModel.find_by_id(file_id, user_id)
        if not file_doc:
            raise NotFoundError("File not found.")

        chunks = await vector_store.get_all_chunks(user_id, file_id)
        if not chunks:
            content = "(no extracted content available for this file)"
        else:
            content = await self._summarize(chunks)

        doc = SummaryModel.doc(
            file_id=file_id,
            user_id=user_id,
            content=content,
            model_used=settings.OPENROUTER_MODEL,
        )
        await SummaryModel.upsert(file_id, doc)
        fresh = await SummaryModel.find_by_file(file_id)
        public = SummaryModel.to_public(fresh) if fresh else SummaryModel.to_public({**doc, "_id": ""})
        await cache_set_json(CACHE_KEY.format(file_id=file_id), public, ttl=SUMMARY_TTL)
        return public

    async def _summarize(self, chunks: list[dict[str, Any]]) -> str:
        joined = "\n\n".join((c.get("text") or "")[:1000] for c in chunks[:30])
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a precise document summarizer. Summarize the supplied "
                    "document excerpts into an overview, 3-7 key bullet points, "
                    "notable people/dates/numbers, and a closing takeaway."
                ),
            },
            {"role": "user", "content": joined},
        ]
        try:
            return await asyncio.wait_for(
                create_chat_completion(messages),
                timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
            )
        except Exception as e:
            logger.exception("summary_failed", error=str(e))
            return "(summary generation failed)"


summary_service = SummaryService()
