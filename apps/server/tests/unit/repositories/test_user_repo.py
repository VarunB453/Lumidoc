"""Unit tests for the UserRepository against an in-memory Mongo (mongomock)."""
from __future__ import annotations

import pytest

from app.models.user import UserModel
from app.repositories.user_repo import UserRepository

pytestmark = pytest.mark.asyncio


async def _seed_user(email: str = "alice@example.com", active: bool = True) -> str:
    doc = UserModel.doc(email, "hashed", "Alice")
    doc["is_active"] = active
    return await UserRepository.insert(doc)


async def test_insert_and_find_by_id():
    user_id = await _seed_user()
    found = await UserRepository.find_by_id(user_id)
    assert found is not None
    assert found["email"] == "alice@example.com"


async def test_find_by_id_invalid_returns_none():
    assert await UserRepository.find_by_id("not-an-object-id") is None


async def test_find_by_email_is_case_insensitive():
    await _seed_user("Bob@Example.com")
    found = await UserRepository.find_by_email("  BOB@example.COM ")
    assert found is not None
    assert found["name"] == "Alice"


async def test_email_exists():
    await _seed_user("carol@example.com")
    assert await UserRepository.email_exists("carol@example.com") is True
    assert await UserRepository.email_exists("nobody@example.com") is False


async def test_update_modifies_fields():
    user_id = await _seed_user("dave@example.com")
    modified = await UserRepository.update(user_id, {"name": "Dave"})
    assert modified is True
    found = await UserRepository.find_by_id(user_id)
    assert found is not None
    assert found["name"] == "Dave"
    assert "updated_at" in found


async def test_delete_removes_document():
    user_id = await _seed_user("erin@example.com")
    assert await UserRepository.delete(user_id) is True
    assert await UserRepository.find_by_id(user_id) is None


async def test_find_active_users_filters_inactive():
    await _seed_user("active1@example.com", active=True)
    await _seed_user("inactive1@example.com", active=False)
    active = await UserRepository.find_active_users()
    emails = {u["email"] for u in active}
    assert "active1@example.com" in emails
    assert "inactive1@example.com" not in emails


async def test_count():
    await _seed_user("count1@example.com")
    await _seed_user("count2@example.com")
    total = await UserRepository.count({})
    assert total >= 2
