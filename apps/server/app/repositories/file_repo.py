"""File repository — data access layer for the files collection."""
from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class FileRepository(BaseRepository):
    """Data access for the `files` collection."""

    collection_name = "files"

    @classmethod
    async def find_by_user(
        cls,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id}
        if not include_deleted:
            query["is_deleted"] = {"$ne": True}
        return await cls.find_many(
            query, skip=skip, limit=limit, sort=[("created_at", -1)]
        )

    @classmethod
    async def count_by_user(cls, user_id: str, include_deleted: bool = False) -> int:
        query: dict[str, Any] = {"user_id": user_id}
        if not include_deleted:
            query["is_deleted"] = {"$ne": True}
        return await cls.count(query)

    @classmethod
    async def find_by_status(
        cls, user_id: str, status: str
    ) -> list[dict[str, Any]]:
        return await cls.find_many(
            {"user_id": user_id, "status": status, "is_deleted": {"$ne": True}},
            sort=[("created_at", -1)],
        )


file_repo = FileRepository()
