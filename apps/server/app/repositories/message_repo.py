"""Message repository — data access layer for the messages collection."""
from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository):
    """Data access for the `messages` collection."""

    collection_name = "messages"

    @classmethod
    async def find_by_conversation(
        cls,
        conversation_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return await cls.find_many(
            {"conversation_id": conversation_id},
            skip=skip,
            limit=limit,
            sort=[("created_at", 1)],  # chronological order
        )

    @classmethod
    async def count_by_conversation(cls, conversation_id: str) -> int:
        return await cls.count({"conversation_id": conversation_id})

    @classmethod
    async def delete_by_conversation(cls, conversation_id: str) -> int:
        """Delete all messages in a conversation. Returns count deleted."""
        result = await cls._collection().delete_many(
            {"conversation_id": conversation_id}
        )
        return result.deleted_count


message_repo = MessageRepository()
