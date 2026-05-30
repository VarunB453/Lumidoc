"""Unit tests for model document builders and public serializers."""
from __future__ import annotations

from bson import ObjectId

from app.models.message import MessageModel
from app.models.user import UserModel


def test_message_doc_defaults_empty_collections():
    doc = MessageModel.doc("conv1", "user1", "user", "hello")
    assert doc["conversation_id"] == "conv1"
    assert doc["role"] == "user"
    assert doc["content"] == "hello"
    assert doc["source_chunks"] == []
    assert doc["timestamp_refs"] == []
    assert doc["created_at"] is not None


def test_message_to_public_stringifies_id():
    oid = ObjectId()
    raw = {
        "_id": oid,
        "conversation_id": "c",
        "user_id": "u",
        "role": "assistant",
        "content": "hi",
        "created_at": "2024-01-01T00:00:00+00:00",
    }
    pub = MessageModel.to_public(raw)
    assert pub["id"] == str(oid)
    assert pub["source_chunks"] == []
    assert pub["timestamp_refs"] == []


def test_user_doc_normalizes_email():
    doc = UserModel.doc("  Alice@Example.COM ", "hashed", "Alice")
    assert doc["email"] == "alice@example.com"
    assert doc["provider"] == "local"
    assert doc["role"] == "user"
    assert doc["is_active"] is True


def test_user_to_public_excludes_password():
    oid = ObjectId()
    raw = UserModel.doc("a@b.com", "secret-hash", "A")
    raw["_id"] = oid
    pub = UserModel.to_public(raw)
    assert pub["id"] == str(oid)
    assert "hashed_password" not in pub
    assert pub["email"] == "a@b.com"
