"""Unit tests for ChatService (with fake LLM + retrieval)."""
from __future__ import annotations

import pytest

from app.core.exceptions import NotFoundError
from app.models.file import FileModel
from app.services.chat_service import ChatService, chat_service
from app.services.vector_store import vector_store


@pytest.mark.asyncio
async def test_create_conversation_validates_file_ownership():
    with pytest.raises(NotFoundError):
        await chat_service.create_conversation("u1", "title", ["nonexistent-file"])


@pytest.mark.asyncio
async def test_create_conversation_success():
    doc = FileModel.doc("u1", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    conv = await chat_service.create_conversation("u1", "My chat", [fid])
    assert conv["title"] == "My chat"
    assert conv["file_ids"] == [fid]


@pytest.mark.asyncio
async def test_list_conversations():
    doc = FileModel.doc("u_list", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    await chat_service.create_conversation("u_list", "C1", [fid])
    await chat_service.create_conversation("u_list", "C2", [fid])
    convs = await chat_service.list_conversations("u_list")
    titles = {c["title"] for c in convs}
    assert {"C1", "C2"}.issubset(titles)


@pytest.mark.asyncio
async def test_get_conversation_not_found():
    with pytest.raises(NotFoundError):
        await chat_service.get_conversation("507f1f77bcf86cd799439011", "u1")


@pytest.mark.asyncio
async def test_answer_and_history():
    doc = FileModel.doc("u_ans", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert(
        "u_ans", fid, [[0.1] * 768], ["context text"], [{"page": 1}]
    )
    conv = await chat_service.create_conversation("u_ans", "C", [fid])
    ai_msg, meta = await chat_service.answer(conv["id"], "u_ans", "What is this?")
    assert ai_msg["role"] == "assistant"
    assert ai_msg["content"]
    assert meta["user_message_id"]
    msgs = await chat_service.list_messages(conv["id"], "u_ans")
    assert len(msgs) == 2


@pytest.mark.asyncio
async def test_answer_no_conversation():
    with pytest.raises(NotFoundError):
        await chat_service.answer("507f1f77bcf86cd799439011", "u1", "q?")


@pytest.mark.asyncio
async def test_stream_answer_yields_events():
    doc = FileModel.doc("u_str", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert(
        "u_str", fid, [[0.1] * 768], ["ctx"], [{"page": 1}]
    )
    conv = await chat_service.create_conversation("u_str", "C", [fid])

    events = []
    async for ev in chat_service.stream_answer(conv["id"], "u_str", "Hello?"):
        events.append(ev["event"])
    assert "user_message" in events
    assert "done" in events
    assert "token" in events


@pytest.mark.asyncio
async def test_stream_answer_missing_conv():
    with pytest.raises(NotFoundError):
        async for _ in chat_service.stream_answer("507f1f77bcf86cd799439011", "u1", "q?"):
            break


def test_extract_timestamp_refs_mm_ss():
    refs = ChatService._extract_timestamp_refs("See at 02:30 and 01:15:45.")
    seconds = {r["seconds"] for r in refs}
    assert 150.0 in seconds  # 02:30
    assert 4545.0 in seconds  # 01:15:45


def test_extract_timestamp_refs_none():
    assert ChatService._extract_timestamp_refs("plain text without time") == []


def test_format_context_empty():
    assert "no relevant" in ChatService._format_context([]).lower()


def test_format_context_with_page_and_time():
    out = ChatService._format_context(
        [
            {"text": "hello", "page": 1},
            {"text": "world", "start_time": 1.0, "end_time": 2.5},
        ]
    )
    assert "page 1" in out
    assert "1.0s" in out


def test_format_history_empty():
    assert "no prior" in ChatService._format_history([]).lower()


def test_format_history_renders():
    out = ChatService._format_history([{"role": "user", "content": "hi"}])
    assert "USER" in out and "hi" in out


@pytest.mark.asyncio
async def test_retrieve_dedup():
    svc = ChatService()
    doc = FileModel.doc("u_ret", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert(
        "u_ret",
        fid,
        [[0.1] * 768, [0.1] * 768],
        ["same text", "same text"],
        [{"page": 1}, {"page": 2}],
    )
    hits = await svc._retrieve("u_ret", [fid], "query")
    # Dedup should remove the duplicate text.
    texts = [h["text"] for h in hits]
    assert len(set(texts)) == len(texts)


@pytest.mark.asyncio
async def test_retrieve_no_files_returns_empty():
    svc = ChatService()
    assert await svc._retrieve("u", [], "q") == []
