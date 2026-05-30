"""Message MongoDB model."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.db.mongodb import get_messages


class MessageModel:
    @staticmethod
    def doc(
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        source_chunks: list[dict[str, Any]] | None = None,
        timestamp_refs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "source_chunks": source_chunks or [],
            "timestamp_refs": timestamp_refs or [],
            "created_at": datetime.now(UTC),
        }

    @staticmethod
    async def insert(doc: dict[str, Any]) -> str:
        result = await get_messages().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    async def list_for_conversation(
        conversation_id: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        cursor = get_messages().find({"conversation_id": conversation_id}).sort("created_at", 1)
        if limit:
            cursor = cursor.limit(limit)
        return [d async for d in cursor]

    @staticmethod
    async def recent_history(
        conversation_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        cursor = (
            get_messages()
            .find({"conversation_id": conversation_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        items = [d async for d in cursor]
        return list(reversed(items))

    @staticmethod
    def to_public(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "conversation_id": doc["conversation_id"],
            "user_id": doc["user_id"],
            "role": doc["role"],
            "content": doc["content"],
            "source_chunks": doc.get("source_chunks", []),
            "timestamp_refs": doc.get("timestamp_refs", []),
            "created_at": doc["created_at"],
        }
