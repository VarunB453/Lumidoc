"""Base model utilities for MongoDB documents."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(UTC)


def new_object_id() -> ObjectId:
    """Generate a new MongoDB ObjectId."""
    return ObjectId()


def serialize_doc(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert a raw MongoDB document to a JSON-serializable dict.

    - Converts _id to string 'id'
    - Converts ObjectId fields (ending in _id) to strings
    - Passes through everything else
    """
    if doc is None:
        return None
    out: dict[str, Any] = {}
    for key, value in doc.items():
        if key == "_id":
            out["id"] = str(value)
        elif isinstance(value, ObjectId):
            out[key] = str(value)
        elif isinstance(value, datetime):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out


def base_document_fields() -> dict[str, Any]:
    """Return common fields for all documents (timestamps)."""
    now = utcnow()
    return {
        "created_at": now,
        "updated_at": now,
    }
