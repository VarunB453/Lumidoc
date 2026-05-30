"""Summary MongoDB model."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.db.mongodb import get_summaries


class SummaryModel:
    @staticmethod
    def doc(
        file_id: str,
        user_id: str,
        content: str,
        model_used: str,
        status: str = "ready",
    ) -> dict[str, Any]:
        return {
            "file_id": file_id,
            "user_id": user_id,
            "content": content,
            "model_used": model_used,
            "status": status,
            "generated_at": datetime.now(UTC),
        }

    @staticmethod
    async def upsert(file_id: str, doc: dict[str, Any]) -> str:
        result = await get_summaries().update_one(
            {"file_id": file_id}, {"$set": doc}, upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        existing = await get_summaries().find_one({"file_id": file_id})
        return str(existing["_id"]) if existing else ""

    @staticmethod
    async def find_by_file(file_id: str) -> dict[str, Any] | None:
        return await get_summaries().find_one({"file_id": file_id})

    @staticmethod
    def to_public(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "file_id": doc["file_id"],
            "user_id": doc["user_id"],
            "content": doc.get("content", ""),
            "status": doc.get("status", "ready"),
            "model_used": doc.get("model_used", ""),
            "generated_at": doc.get("generated_at"),
        }
