"""Timestamp extraction service: identify topic segments from transcripts."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.db.redis_client import cache_get_json, cache_set_json
from app.integrations.openrouter_client import create_chat_completion
from app.models.file import FileModel
from app.models.timestamp import TimestampModel
from app.services.vector_store import vector_store

logger = get_logger("timestamp")

TIMESTAMP_TTL = 43200  # 12h
CACHE_KEY = "timestamps:{file_id}"

SYSTEM_PROMPT = (
    "You are a precise transcript-segmentation assistant. Given a list of transcript "
    "segments with start/end times in seconds, group them into topic segments. "
    "Return strict JSON only with shape: "
    '{"topics": [{"topic": str, "start_time": float, "end_time": float, "summary": str}]}. '
    "Topics should be coherent themes, start_time must be <= end_time, and topic titles "
    "must be short."
)


class TimestampService:
    """Extract topic-level timestamps from audio/video transcripts."""

    async def get_cached_or_generate(self, file_id: str, user_id: str) -> list[dict[str, Any]]:
        cache_key = CACHE_KEY.format(file_id=file_id)
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        existing = await TimestampModel.list_for_file(file_id)
        if existing:
            public = [TimestampModel.to_public(d) for d in existing]
            await cache_set_json(cache_key, public, ttl=TIMESTAMP_TTL)
            return public
        return await self.generate(file_id, user_id)

    async def generate(self, file_id: str, user_id: str) -> list[dict[str, Any]]:
        file_doc = await FileModel.find_by_id(file_id, user_id)
        if not file_doc:
            raise NotFoundError("File not found.")
        if file_doc.get("file_type") not in {"audio", "video"}:
            raise ValidationError("Timestamp extraction requires audio or video files.")

        chunks = await vector_store.get_all_chunks(user_id, file_id)
        timestamped = [
            c for c in chunks if c.get("start_time") is not None and c.get("end_time") is not None
        ]
        if not timestamped:
            raise NotFoundError("No timestamped transcript content found for this file.")

        topics = await self._call_llm(timestamped)
        topics = self._sanitize(topics, timestamped)

        await TimestampModel.delete_for_file(file_id)
        docs = [
            TimestampModel.doc(
                file_id=file_id,
                user_id=user_id,
                topic=t["topic"],
                start_time=t["start_time"],
                end_time=t["end_time"],
                summary=t.get("summary", ""),
            )
            for t in topics
        ]
        if docs:
            await TimestampModel.insert_many(docs)

        fresh = await TimestampModel.list_for_file(file_id)
        public = [TimestampModel.to_public(d) for d in fresh]
        await cache_set_json(CACHE_KEY.format(file_id=file_id), public, ttl=TIMESTAMP_TTL)
        return public

    async def _call_llm(self, timestamped_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = [
            f"[{float(c['start_time']):.1f}-{float(c['end_time']):.1f}] {c.get('text','')[:300]}"
            for c in timestamped_chunks
        ]
        joined = "\n".join(rows)[:25000]
        try:
            raw = await asyncio.wait_for(
                create_chat_completion(
                    [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": joined},
                    ]
                ),
                timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
            )
            data = json.loads(raw or "{}")
            topics = data.get("topics", [])
            if not isinstance(topics, list):
                return []
            return topics
        except Exception as e:
            logger.exception("topic_extraction_failed", error=str(e))
            return []

    @staticmethod
    def _sanitize(
        topics: list[dict[str, Any]], chunks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Clamp times into the actual transcript range, dedupe, sort."""
        if not chunks:
            return []
        min_t = min(float(c["start_time"]) for c in chunks)
        max_t = max(float(c["end_time"]) for c in chunks)
        out: list[dict[str, Any]] = []
        seen: set[tuple[float, float]] = set()
        for t in topics:
            try:
                topic = str(t.get("topic", "")).strip()[:300]
                start = max(min_t, float(t.get("start_time", 0)))
                end = min(max_t, float(t.get("end_time", 0)))
                summary = str(t.get("summary", "")).strip()
            except (TypeError, ValueError):
                continue
            if not topic or end < start:
                continue
            key = (round(start, 2), round(end, 2))
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {"topic": topic, "start_time": start, "end_time": end, "summary": summary}
            )
        out.sort(key=lambda x: x["start_time"])
        return out

    async def search(self, file_id: str, query: str) -> list[dict[str, Any]]:
        docs = await TimestampModel.search_topic(file_id, query)
        return [TimestampModel.to_public(d) for d in docs]


timestamp_service = TimestampService()
