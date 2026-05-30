"""Unit tests for TimestampService."""
from __future__ import annotations

import pytest

from app.core.exceptions import NotFoundError, ValidationError
from app.models.file import FileModel
from app.services.timestamp_service import timestamp_service
from app.services.vector_store import vector_store


@pytest.mark.asyncio
async def test_generate_no_file_raises():
    with pytest.raises(NotFoundError):
        await timestamp_service.generate("missing", "u1")


@pytest.mark.asyncio
async def test_generate_rejects_pdf():
    doc = FileModel.doc("u1", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    with pytest.raises(ValidationError):
        await timestamp_service.generate(fid, "u1")


@pytest.mark.asyncio
async def test_generate_no_timestamped_chunks_raises():
    doc = FileModel.doc("u1", "x.mp3", "x.mp3", "audio", "k", 10)
    fid = await FileModel.insert(doc)
    # Insert chunks with no start/end metadata.
    await vector_store.upsert("u1", fid, [[0.1] * 768], ["text"], [{}])
    with pytest.raises(NotFoundError):
        await timestamp_service.generate(fid, "u1")


@pytest.mark.asyncio
async def test_generate_audio_success():
    doc = FileModel.doc("u1", "x.mp3", "x.mp3", "audio", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert(
        "u1",
        fid,
        [[0.1] * 768, [0.2] * 768],
        ["intro text", "more text"],
        [{"start_time": 0.0, "end_time": 30.0}, {"start_time": 30.0, "end_time": 60.0}],
    )
    entries = await timestamp_service.generate(fid, "u1")
    assert len(entries) >= 1
    assert entries[0]["topic"]


@pytest.mark.asyncio
async def test_sanitize_clamps_times():
    chunks = [{"start_time": 10.0, "end_time": 100.0}]
    topics = [
        {"topic": "T1", "start_time": -5, "end_time": 200, "summary": "s"},
        {"topic": "T2", "start_time": 50, "end_time": 30, "summary": "bad"},  # invalid
        {"topic": "", "start_time": 20, "end_time": 30, "summary": ""},  # blank topic
    ]
    out = timestamp_service._sanitize(topics, chunks)
    assert len(out) == 1
    assert out[0]["start_time"] == 10.0
    assert out[0]["end_time"] == 100.0


def test_sanitize_empty_chunks():
    assert timestamp_service._sanitize([{"topic": "x", "start_time": 0, "end_time": 1}], []) == []


@pytest.mark.asyncio
async def test_search_returns_entries():
    doc = FileModel.doc("u1", "x.mp3", "x.mp3", "audio", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert(
        "u1",
        fid,
        [[0.1] * 768],
        ["hello"],
        [{"start_time": 0.0, "end_time": 10.0}],
    )
    await timestamp_service.generate(fid, "u1")
    found = await timestamp_service.search(fid, "Intro")
    assert isinstance(found, list)


@pytest.mark.asyncio
async def test_get_cached_or_generate_returns_existing():
    doc = FileModel.doc("u1", "x.mp3", "x.mp3", "audio", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert(
        "u1", fid, [[0.1] * 768], ["t"], [{"start_time": 0.0, "end_time": 5.0}]
    )
    first = await timestamp_service.generate(fid, "u1")
    cached = await timestamp_service.get_cached_or_generate(fid, "u1")
    assert len(cached) == len(first)
