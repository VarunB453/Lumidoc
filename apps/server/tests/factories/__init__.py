"""Test factories for generating model instances."""
from __future__ import annotations

from datetime import UTC, datetime, timezone
from typing import Any

from bson import ObjectId


def make_user(
    email: str = "test@example.com",
    name: str = "Test User",
    role: str = "user",
    provider: str = "local",
    is_active: bool = True,
    **overrides: Any,
) -> dict[str, Any]:
    """Create a user document for testing."""
    doc = {
        "_id": ObjectId(),
        "email": email,
        "hashed_password": "$2b$12$fakehash",
        "name": name,
        "avatar_url": None,
        "role": role,
        "provider": provider,
        "is_active": is_active,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    doc.update(overrides)
    return doc


def make_file(
    user_id: str = "507f1f77bcf86cd799439011",
    filename: str = "test.pdf",
    status: str = "ready",
    **overrides: Any,
) -> dict[str, Any]:
    """Create a file document for testing."""
    doc = {
        "_id": ObjectId(),
        "user_id": user_id,
        "filename": filename,
        "original_name": filename,
        "mime_type": "application/pdf",
        "size_bytes": 1024,
        "status": status,
        "is_deleted": False,
        "storage_key": f"files/{user_id}/{filename}",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    doc.update(overrides)
    return doc


def make_conversation(
    user_id: str = "507f1f77bcf86cd799439011",
    title: str = "Test Conversation",
    **overrides: Any,
) -> dict[str, Any]:
    """Create a conversation document for testing."""
    doc = {
        "_id": ObjectId(),
        "user_id": user_id,
        "title": title,
        "file_ids": [],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    doc.update(overrides)
    return doc


def make_message(
    conversation_id: str = "507f1f77bcf86cd799439011",
    role: str = "user",
    content: str = "Hello, world!",
    **overrides: Any,
) -> dict[str, Any]:
    """Create a message document for testing."""
    doc = {
        "_id": ObjectId(),
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(UTC),
    }
    doc.update(overrides)
    return doc
