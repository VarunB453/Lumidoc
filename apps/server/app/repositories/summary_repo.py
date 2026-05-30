"""Summary repository — data access layer for the summaries collection."""
from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class SummaryRepository(BaseRepository):
    """Data access for the `summaries` collection."""

    collection_name = "summaries"

    @classmethod
    async def find_by_file(cls, file_id: str) -> dict[str, Any] | None:
        return await cls.find_one({"file_id": file_id})

    @classmethod
    async def upsert_by_file(cls, file_id: str, data: dict[str, Any]) -> str:
        """Insert or update a summary for a given file."""
        existing = await cls.find_by_file(file_id)
        if existing:
            await cls.update(str(existing["_id"]), data)
            return str(existing["_id"])
        data["file_id"] = file_id
        return await cls.insert(data)


summary_repo = SummaryRepository()
