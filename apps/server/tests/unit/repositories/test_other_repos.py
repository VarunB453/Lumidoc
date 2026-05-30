"""Unit tests for conversation/file/message/summary/timestamp repositories
against an in-memory Mongo (mongomock)."""
from __future__ import annotations

import pytest

from app.repositories.conversation_repo import ConversationRepository
from app.repositories.file_repo import FileRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.summary_repo import SummaryRepository
from app.repositories.timestamp_repo import TimestampRepository

pytestmark = pytest.mark.asyncio


# --------------------------- conversations ---------------------------
async def test_conversation_find_and_count_by_user():
    await ConversationRepository.insert({"user_id": "u1", "title": "A"})
    await ConversationRepository.insert({"user_id": "u1", "title": "B"})
    await ConversationRepository.insert({"user_id": "u2", "title": "C"})

    items = await ConversationRepository.find_by_user("u1")
    assert len(items) == 2
    assert await ConversationRepository.count_by_user("u1") == 2
    assert await ConversationRepository.count_by_user("u2") == 1


# --------------------------- files ---------------------------
async def test_file_find_by_user_excludes_deleted_by_default():
    await FileRepository.insert({"user_id": "u1", "status": "ready"})
    await FileRepository.insert({"user_id": "u1", "status": "ready", "is_deleted": True})

    visible = await FileRepository.find_by_user("u1")
    assert len(visible) == 1
    assert await FileRepository.count_by_user("u1") == 1

    all_files = await FileRepository.find_by_user("u1", include_deleted=True)
    assert len(all_files) == 2
    assert await FileRepository.count_by_user("u1", include_deleted=True) == 2


async def test_file_find_by_status():
    await FileRepository.insert({"user_id": "u1", "status": "ready"})
    await FileRepository.insert({"user_id": "u1", "status": "processing"})
    ready = await FileRepository.find_by_status("u1", "ready")
    assert len(ready) == 1
    assert ready[0]["status"] == "ready"


# --------------------------- messages ---------------------------
async def test_message_find_count_and_delete_by_conversation():
    for i in range(3):
        await MessageRepository.insert(
            {"conversation_id": "c1", "user_id": "u1", "content": f"m{i}"}
        )
    await MessageRepository.insert(
        {"conversation_id": "c2", "user_id": "u1", "content": "other"}
    )

    msgs = await MessageRepository.find_by_conversation("c1")
    assert len(msgs) == 3
    assert await MessageRepository.count_by_conversation("c1") == 3

    deleted = await MessageRepository.delete_by_conversation("c1")
    assert deleted == 3
    assert await MessageRepository.count_by_conversation("c1") == 0
    assert await MessageRepository.count_by_conversation("c2") == 1


# --------------------------- summaries ---------------------------
async def test_summary_upsert_inserts_then_updates():
    sid = await SummaryRepository.upsert_by_file("f1", {"content": "v1", "status": "ready"})
    found = await SummaryRepository.find_by_file("f1")
    assert found is not None
    assert found["content"] == "v1"

    sid2 = await SummaryRepository.upsert_by_file("f1", {"content": "v2"})
    assert sid2 == sid
    found2 = await SummaryRepository.find_by_file("f1")
    assert found2 is not None
    assert found2["content"] == "v2"


# --------------------------- timestamps ---------------------------
async def test_timestamp_bulk_insert_find_and_delete():
    assert await TimestampRepository.bulk_insert([]) == 0

    docs = [
        {"file_id": "f1", "start_time": 10.0, "topic": "B"},
        {"file_id": "f1", "start_time": 1.0, "topic": "A"},
    ]
    inserted = await TimestampRepository.bulk_insert(docs)
    assert inserted == 2

    found = await TimestampRepository.find_by_file("f1")
    assert [d["topic"] for d in found] == ["A", "B"]  # sorted by start_time

    deleted = await TimestampRepository.delete_by_file("f1")
    assert deleted == 2
    assert await TimestampRepository.find_by_file("f1") == []
