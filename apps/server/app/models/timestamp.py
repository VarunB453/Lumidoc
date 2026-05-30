"""Timestamp MongoDB model."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.db.mongodb import get_timestamps


class TimestampModel:
    @staticmethod
    def doc(
        file_id: str,
        user_id: str,
        topic: str,
        start_time: float,
        end_time: float,
        summary: str = "",
    ) -> dict[str, Any]:
        return {
            "file_id": file_id,
            "user_id": user_id,
            "topic": topic,
            "start_time": float(start_time),
            "end_time": float(end_time),
            "summary": summary,
            "created_at": datetime.now(UTC),
        }

    @staticmethod
    async def insert_many(docs: list[dict[str, Any]]) -> list[str]:
        if not docs:
            return []
        result = await get_timestamps().insert_many(docs)
        return [str(_id) for _id in result.inserted_ids]

    @staticmethod
    async def delete_for_file(file_id: str) -> None:
        await get_timestamps().delete_many({"file_id": file_id})

    @staticmethod
    async def list_for_file(file_id: str) -> list[dict[str, Any]]:
        cursor = get_timestamps().find({"file_id": file_id}).sort("start_time", 1)
        return [d async for d in cursor]

    @staticmethod
    async def search_topic(file_id: str, topic_query: str) -> list[dict[str, Any]]:
        regex = {"$regex": topic_query, "$options": "i"}
        cursor = (
            get_timestamps()
            .find({"file_id": file_id, "topic": regex})
            .sort("start_time", 1)
        )
        return [d async for d in cursor]

    @staticmethod
    def to_public(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "file_id": doc["file_id"],
            "user_id": doc.get("user_id"),
            "topic": doc["topic"],
            "start_time": doc["start_time"],
            "end_time": doc["end_time"],
            "summary": doc.get("summary", ""),
            "created_at": doc.get("created_at"),
        }
