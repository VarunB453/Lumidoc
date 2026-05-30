"""Timestamp repository — data access layer for timestamp_entries collection."""
from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class TimestampRepository(BaseRepository):
    """Data access for the `timestamp_entries` collection."""

    collection_name = "timestamp_entries"

    @classmethod
    async def find_by_file(
        cls, file_id: str, skip: int = 0, limit: int = 500
    ) -> list[dict[str, Any]]:
        return await cls.find_many(
            {"file_id": file_id},
            skip=skip,
            limit=limit,
            sort=[("start_time", 1)],
        )

    @classmethod
    async def delete_by_file(cls, file_id: str) -> int:
        """Delete all timestamps for a file. Returns count deleted."""
        result = await cls._collection().delete_many({"file_id": file_id})
        return result.deleted_count

    @classmethod
    async def bulk_insert(cls, docs: list[dict[str, Any]]) -> int:
        """Insert multiple timestamp entries. Returns count inserted."""
        if not docs:
            return 0
        result = await cls._collection().insert_many(docs)
        return len(result.inserted_ids)


timestamp_repo = TimestampRepository()
