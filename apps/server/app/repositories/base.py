"""Base repository with common CRUD operations for MongoDB collections."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.logging import get_logger
from app.db.mongodb import MongoDB

logger = get_logger("repository")


class BaseRepository:
    """Generic repository providing common MongoDB CRUD operations."""

    collection_name: str = ""

    @classmethod
    def _collection(cls) -> AsyncIOMotorCollection:
        return MongoDB.get_collection(cls.collection_name)

    @classmethod
    async def find_by_id(cls, doc_id: str) -> dict[str, Any] | None:
        """Find a document by its ObjectId string."""
        try:
            oid = ObjectId(doc_id)
        except Exception:
            return None
        return await cls._collection().find_one({"_id": oid})

    @classmethod
    async def find_one(cls, query: dict[str, Any]) -> dict[str, Any] | None:
        """Find a single document matching the query."""
        return await cls._collection().find_one(query)

    @classmethod
    async def find_many(
        cls,
        query: dict[str, Any],
        skip: int = 0,
        limit: int = 50,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[dict[str, Any]]:
        """Find multiple documents with pagination and optional sorting."""
        cursor = cls._collection().find(query).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=limit)

    @classmethod
    async def count(cls, query: dict[str, Any]) -> int:
        """Count documents matching the query."""
        return await cls._collection().count_documents(query)

    @classmethod
    async def insert(cls, doc: dict[str, Any]) -> str:
        """Insert a document and return its string ID."""
        result = await cls._collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    async def update(cls, doc_id: str, fields: dict[str, Any]) -> bool:
        """Update a document by ID. Returns True if modified."""
        fields["updated_at"] = datetime.now(UTC)
        result = await cls._collection().update_one(
            {"_id": ObjectId(doc_id)}, {"$set": fields}
        )
        return result.modified_count > 0

    @classmethod
    async def delete(cls, doc_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted."""
        result = await cls._collection().delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0

    @classmethod
    async def soft_delete(cls, doc_id: str) -> bool:
        """Soft-delete by setting is_deleted=True."""
        return await cls.update(doc_id, {"is_deleted": True})
