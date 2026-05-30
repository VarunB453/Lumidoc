"""Conversation MongoDB model."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from app.db.mongodb import get_conversations


class ConversationModel:
    @staticmethod
    def doc(user_id: str, title: str, file_ids: list[str]) -> dict[str, Any]:
        now = datetime.now(UTC)
        return {
            "user_id": user_id,
            "title": title,
            "file_ids": file_ids,
            "message_count": 0,
            "is_favorite": False,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
        }

    @staticmethod
    async def insert(doc: dict[str, Any]) -> str:
        result = await get_conversations().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    async def find_by_id(conv_id: str, user_id: str | None = None) -> dict[str, Any] | None:
        try:
            oid = ObjectId(conv_id)
        except Exception:
            return None
        query: dict[str, Any] = {"_id": oid, "is_deleted": {"$ne": True}}
        if user_id:
            query["user_id"] = user_id
        return await get_conversations().find_one(query)

    @staticmethod
    async def list_for_user(
        user_id: str, only_favorites: bool = False
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id, "is_deleted": {"$ne": True}}
        if only_favorites:
            query["is_favorite"] = True
        cursor = get_conversations().find(query).sort("updated_at", -1)
        return [d async for d in cursor]

    @staticmethod
    async def update_fields(
        conv_id: str, user_id: str, fields: dict[str, Any]
    ) -> dict[str, Any] | None:
        try:
            oid = ObjectId(conv_id)
        except Exception:
            return None
        fields["updated_at"] = datetime.now(UTC)
        await get_conversations().update_one(
            {"_id": oid, "user_id": user_id, "is_deleted": {"$ne": True}},
            {"$set": fields},
        )
        return await get_conversations().find_one({"_id": oid, "user_id": user_id})

    @staticmethod
    async def soft_delete(conv_id: str, user_id: str) -> bool:
        try:
            oid = ObjectId(conv_id)
        except Exception:
            return False
        result = await get_conversations().update_one(
            {"_id": oid, "user_id": user_id},
            {
                "$set": {
                    "is_deleted": True,
                    "deleted_at": datetime.now(UTC),
                }
            },
        )
        return result.modified_count > 0

    @staticmethod
    async def bump(conv_id: str, *, increment_messages: int = 0) -> None:
        update: dict[str, Any] = {"$set": {"updated_at": datetime.now(UTC)}}
        if increment_messages:
            update["$inc"] = {"message_count": increment_messages}
        await get_conversations().update_one({"_id": ObjectId(conv_id)}, update)

    @staticmethod
    def to_public(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "title": doc.get("title", "New conversation"),
            "file_ids": doc.get("file_ids", []),
            "message_count": doc.get("message_count", 0),
            "is_favorite": bool(doc.get("is_favorite", False)),
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"],
        }
