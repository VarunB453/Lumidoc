"""User MongoDB model (plain dict via Motor)."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from app.db.mongodb import get_users


class UserModel:
    """Static helpers around the `users` collection."""

    @staticmethod
    def doc(
        email: str,
        hashed_password: str | None,
        name: str,
        avatar_url: str | None = None,
        role: str = "user",
        provider: str = "local",
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        return {
            "email": email.lower().strip(),
            "hashed_password": hashed_password,
            "name": name,
            "avatar_url": avatar_url,
            "role": role,
            "provider": provider,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

    @staticmethod
    async def find_by_email(email: str) -> dict[str, Any] | None:
        return await get_users().find_one({"email": email.lower().strip()})

    @staticmethod
    async def find_by_id(user_id: str) -> dict[str, Any] | None:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        return await get_users().find_one({"_id": oid})

    @staticmethod
    async def insert(doc: dict[str, Any]) -> str:
        result = await get_users().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    async def update(user_id: str, fields: dict[str, Any]) -> None:
        fields["updated_at"] = datetime.now(UTC)
        await get_users().update_one({"_id": ObjectId(user_id)}, {"$set": fields})

    @staticmethod
    def to_public(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "email": doc["email"],
            "name": doc.get("name", ""),
            "avatar_url": doc.get("avatar_url"),
            "role": doc.get("role", "user"),
            "is_active": doc.get("is_active", True),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }
