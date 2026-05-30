"""User repository — data access layer for the users collection."""
from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Data access for the `users` collection."""

    collection_name = "users"

    @classmethod
    async def find_by_email(cls, email: str) -> dict[str, Any] | None:
        return await cls.find_one({"email": email.lower().strip()})

    @classmethod
    async def email_exists(cls, email: str) -> bool:
        doc = await cls.find_by_email(email)
        return doc is not None

    @classmethod
    async def find_active_users(
        cls, skip: int = 0, limit: int = 50
    ) -> list[dict[str, Any]]:
        return await cls.find_many(
            {"is_active": True},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )


user_repo = UserRepository()
