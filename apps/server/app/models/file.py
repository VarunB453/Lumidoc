"""File MongoDB model."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from app.db.mongodb import get_files


class FileModel:
    @staticmethod
    def doc(
        user_id: str,
        filename: str,
        original_name: str,
        file_type: str,
        s3_key: str,
        size_bytes: int,
        mime_type: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        return {
            "user_id": user_id,
            "filename": filename,
            "original_name": original_name,
            "file_type": file_type,
            "s3_key": s3_key,
            "size_bytes": size_bytes,
            "mime_type": mime_type,
            "status": "pending",
            "error_message": None,
            "duration_seconds": None,
            "page_count": None,
            "created_at": now,
            "processed_at": None,
            "is_deleted": False,
        }

    @staticmethod
    async def insert(doc: dict[str, Any]) -> str:
        result = await get_files().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    async def find_by_id(file_id: str, user_id: str | None = None) -> dict[str, Any] | None:
        try:
            oid = ObjectId(file_id)
        except Exception:
            return None
        query: dict[str, Any] = {"_id": oid, "is_deleted": False}
        if user_id:
            query["user_id"] = user_id
        return await get_files().find_one(query)

    @staticmethod
    async def find_by_s3_key(s3_key: str, user_id: str) -> dict[str, Any] | None:
        return await get_files().find_one(
            {"s3_key": s3_key, "user_id": user_id, "is_deleted": False}
        )

    @staticmethod
    async def list_for_user(
        user_id: str, page: int = 1, page_size: int = 20, status: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        query: dict[str, Any] = {"user_id": user_id, "is_deleted": False}
        if status:
            query["status"] = status
        total = await get_files().count_documents(query)
        skip = (page - 1) * page_size
        cursor = (
            get_files()
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        items = [d async for d in cursor]
        return items, total

    @staticmethod
    async def update_status(
        file_id: str,
        status: str,
        error_message: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        fields: dict[str, Any] = {"status": status}
        if error_message is not None:
            fields["error_message"] = error_message
        if status == "ready":
            fields["processed_at"] = datetime.now(UTC)
        if extra:
            fields.update(extra)
        await get_files().update_one({"_id": ObjectId(file_id)}, {"$set": fields})

    @staticmethod
    async def soft_delete(file_id: str, user_id: str) -> bool:
        result = await get_files().update_one(
            {"_id": ObjectId(file_id), "user_id": user_id},
            {"$set": {"is_deleted": True, "deleted_at": datetime.now(UTC)}},
        )
        return result.modified_count > 0

    @staticmethod
    def to_public(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "filename": doc["filename"],
            "original_name": doc["original_name"],
            "file_type": doc["file_type"],
            "s3_key": doc["s3_key"],
            "size_bytes": doc["size_bytes"],
            "status": doc["status"],
            "error_message": doc.get("error_message"),
            "mime_type": doc.get("mime_type"),
            "duration_seconds": doc.get("duration_seconds"),
            "page_count": doc.get("page_count"),
            "created_at": doc.get("created_at"),
            "processed_at": doc.get("processed_at"),
            "is_deleted": doc.get("is_deleted", False),
        }
