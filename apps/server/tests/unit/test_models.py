"""Unit tests for MongoDB model helpers."""
from __future__ import annotations

import pytest

from app.models.conversation import ConversationModel
from app.models.file import FileModel
from app.models.message import MessageModel
from app.models.summary import SummaryModel
from app.models.timestamp import TimestampModel
from app.models.user import UserModel


@pytest.mark.asyncio
async def test_user_model_crud():
    doc = UserModel.doc("u@x.com", "hash", "Name")
    uid = await UserModel.insert(doc)
    assert uid

    found = await UserModel.find_by_email("u@x.com")
    assert found is not None
    assert found["name"] == "Name"

    found_by_id = await UserModel.find_by_id(uid)
    assert found_by_id is not None

    await UserModel.update(uid, {"name": "Updated"})
    refreshed = await UserModel.find_by_id(uid)
    assert refreshed["name"] == "Updated"

    public = UserModel.to_public(refreshed)
    assert public["id"] == uid
    assert public["email"] == "u@x.com"


@pytest.mark.asyncio
async def test_user_find_by_invalid_id():
    assert await UserModel.find_by_id("not-an-objectid") is None


@pytest.mark.asyncio
async def test_file_model_crud():
    doc = FileModel.doc("user1", "abc.pdf", "orig.pdf", "pdf", "s3/key", 100, "application/pdf")
    fid = await FileModel.insert(doc)
    found = await FileModel.find_by_id(fid, "user1")
    assert found["filename"] == "abc.pdf"

    # Status update
    await FileModel.update_status(fid, "ready", extra={"page_count": 5})
    refreshed = await FileModel.find_by_id(fid, "user1")
    assert refreshed["status"] == "ready"
    assert refreshed["page_count"] == 5
    assert refreshed["processed_at"] is not None

    # List
    items, total = await FileModel.list_for_user("user1")
    assert total >= 1
    assert items[0]["filename"] == "abc.pdf"

    # Soft delete
    ok = await FileModel.soft_delete(fid, "user1")
    assert ok
    assert await FileModel.find_by_id(fid, "user1") is None


@pytest.mark.asyncio
async def test_file_model_list_with_status_filter():
    for i, status in enumerate(["pending", "ready", "ready"]):
        doc = FileModel.doc("u2", f"f{i}.pdf", f"o{i}.pdf", "pdf", f"key{i}", 1)
        fid = await FileModel.insert(doc)
        if status != "pending":
            await FileModel.update_status(fid, status)
    items, total = await FileModel.list_for_user("u2", status="ready")
    assert total == 2


@pytest.mark.asyncio
async def test_file_find_invalid_id():
    assert await FileModel.find_by_id("bad-id") is None


@pytest.mark.asyncio
async def test_file_update_status_error_message():
    doc = FileModel.doc("user1", "x.pdf", "x.pdf", "pdf", "key", 1)
    fid = await FileModel.insert(doc)
    await FileModel.update_status(fid, "failed", error_message="boom")
    refreshed = await FileModel.find_by_id(fid, "user1")
    assert refreshed["status"] == "failed"
    assert refreshed["error_message"] == "boom"


@pytest.mark.asyncio
async def test_conversation_model_crud():
    doc = ConversationModel.doc("u1", "Title", ["f1", "f2"])
    cid = await ConversationModel.insert(doc)
    found = await ConversationModel.find_by_id(cid, "u1")
    assert found["title"] == "Title"

    convs = await ConversationModel.list_for_user("u1")
    assert any(c["title"] == "Title" for c in convs)

    await ConversationModel.bump(cid, increment_messages=2)
    refreshed = await ConversationModel.find_by_id(cid, "u1")
    assert refreshed["message_count"] == 2

    public = ConversationModel.to_public(refreshed)
    assert public["id"] == cid


@pytest.mark.asyncio
async def test_conversation_find_invalid_id():
    assert await ConversationModel.find_by_id("bad") is None


@pytest.mark.asyncio
async def test_message_model_crud():
    doc = MessageModel.doc("conv1", "u1", "user", "hi", [], [])
    mid = await MessageModel.insert(doc)
    assert mid

    msgs = await MessageModel.list_for_conversation("conv1")
    assert len(msgs) == 1

    for i in range(3):
        await MessageModel.insert(MessageModel.doc("conv1", "u1", "user", f"m{i}"))
    recent = await MessageModel.recent_history("conv1", limit=2)
    assert len(recent) == 2

    public = MessageModel.to_public(msgs[0])
    assert public["role"] == "user"


@pytest.mark.asyncio
async def test_message_list_with_limit():
    for i in range(5):
        await MessageModel.insert(MessageModel.doc("convL", "u", "user", f"x{i}"))
    msgs = await MessageModel.list_for_conversation("convL", limit=3)
    assert len(msgs) == 3


@pytest.mark.asyncio
async def test_summary_model_upsert():
    doc = SummaryModel.doc("f1", "u1", "Summary text.", "gpt-4o")
    sid = await SummaryModel.upsert("f1", doc)
    assert sid

    found = await SummaryModel.find_by_file("f1")
    assert found["content"] == "Summary text."

    # Upsert again replaces.
    doc2 = SummaryModel.doc("f1", "u1", "Updated.", "gpt-4o")
    await SummaryModel.upsert("f1", doc2)
    found = await SummaryModel.find_by_file("f1")
    assert found["content"] == "Updated."

    public = SummaryModel.to_public(found)
    assert public["file_id"] == "f1"


@pytest.mark.asyncio
async def test_summary_find_missing():
    assert await SummaryModel.find_by_file("missing") is None


@pytest.mark.asyncio
async def test_timestamp_model_crud():
    docs = [
        TimestampModel.doc("f1", "u1", "Intro", 0.0, 30.0, "intro"),
        TimestampModel.doc("f1", "u1", "Main", 30.0, 120.0, "main"),
    ]
    ids = await TimestampModel.insert_many(docs)
    assert len(ids) == 2

    entries = await TimestampModel.list_for_file("f1")
    assert len(entries) == 2

    matches = await TimestampModel.search_topic("f1", "intro")
    assert len(matches) == 1
    assert matches[0]["topic"] == "Intro"

    public = TimestampModel.to_public(entries[0])
    assert public["topic"] in {"Intro", "Main"}

    # Delete
    await TimestampModel.delete_for_file("f1")
    assert await TimestampModel.list_for_file("f1") == []


@pytest.mark.asyncio
async def test_timestamp_insert_empty():
    assert await TimestampModel.insert_many([]) == []
