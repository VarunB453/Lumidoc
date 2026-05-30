"""Conversation repository — data access layer for conversations collection."""
from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository):
    """Data access for the `conversations` collection."""

    collection_name = "conversations"

    @classmethod
    async def find_by_user(
        cls, user_id: str, skip: int = 0, limit: int = 50
    ) -> list[dict[str, Any]]:
        return await cls.find_many(
            {"user_id": user_id},
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)],
        )

    @classmethod
    async def count_by_user(cls, user_id: str) -> int:
        return await cls.count({"user_id": user_id})


conversation_repo = ConversationRepository()
