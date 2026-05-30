"""MongoDB async client (Motor) with collection helpers + index bootstrap."""
from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("mongodb")


class MongoDB:
    """Singleton container for the Motor client + database handle."""

    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls, url: str | None = None, db_name: str | None = None) -> None:
        if cls.client is not None:
            return
        cls.client = AsyncIOMotorClient(
            url or settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            uuidRepresentation="standard",
        )
        cls.db = cls.client[db_name or settings.MONGODB_DB_NAME]
        logger.info("mongodb_connected", db=cls.db.name)

    @classmethod
    async def disconnect(cls) -> None:
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("mongodb_disconnected")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls.db is None:
            raise RuntimeError("MongoDB is not initialized. Call MongoDB.connect() first.")
        return cls.db

    @classmethod
    def get_collection(cls, name: str) -> AsyncIOMotorCollection:
        return cls.get_db()[name]


async def ensure_indexes() -> None:
    """Create all required indexes (idempotent)."""
    db = MongoDB.get_db()

    await db["users"].create_indexes(
        [
            IndexModel([("email", ASCENDING)], unique=True, name="uniq_email"),
            IndexModel([("created_at", DESCENDING)], name="users_created"),
        ]
    )
    await db["files"].create_indexes(
        [
            IndexModel([("user_id", ASCENDING), ("status", ASCENDING)], name="files_user_status"),
            IndexModel([("created_at", DESCENDING)], name="files_created"),
            IndexModel([("user_id", ASCENDING), ("is_deleted", ASCENDING)], name="files_user_del"),
        ]
    )
    await db["conversations"].create_indexes(
        [
            IndexModel([("user_id", ASCENDING)], name="conv_user"),
            IndexModel([("updated_at", DESCENDING)], name="conv_updated"),
        ]
    )
    await db["messages"].create_indexes(
        [
            IndexModel(
                [("conversation_id", ASCENDING), ("created_at", ASCENDING)],
                name="msg_conv_time",
            ),
        ]
    )
    await db["summaries"].create_indexes(
        [
            IndexModel([("file_id", ASCENDING)], unique=True, name="summaries_file"),
        ]
    )
    await db["timestamp_entries"].create_indexes(
        [
            IndexModel(
                [("file_id", ASCENDING), ("start_time", ASCENDING)], name="ts_file_start"
            ),
        ]
    )
    logger.info("mongodb_indexes_ensured")


def get_users() -> AsyncIOMotorCollection:
    return MongoDB.get_collection("users")


def get_files() -> AsyncIOMotorCollection:
    return MongoDB.get_collection("files")


def get_conversations() -> AsyncIOMotorCollection:
    return MongoDB.get_collection("conversations")


def get_messages() -> AsyncIOMotorCollection:
    return MongoDB.get_collection("messages")


def get_summaries() -> AsyncIOMotorCollection:
    return MongoDB.get_collection("summaries")


def get_timestamps() -> AsyncIOMotorCollection:
    return MongoDB.get_collection("timestamp_entries")


def serialize_mongo(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert ObjectId / datetimes to JSON-friendly types in-place."""
    if doc is None:
        return None
    out: dict[str, Any] = {}
    for k, v in doc.items():
        if k == "_id":
            out["id"] = str(v)
        else:
            out[k] = str(v) if k.endswith("_id") and not isinstance(v, list) else v
    return out
