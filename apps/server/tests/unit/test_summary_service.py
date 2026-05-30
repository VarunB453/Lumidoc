"""Unit tests for SummaryService (with fake _summarize)."""
from __future__ import annotations

import pytest

from app.core.exceptions import NotFoundError
from app.models.file import FileModel
from app.services.summary_service import summary_service
from app.services.vector_store import vector_store


@pytest.mark.asyncio
async def test_generate_no_file_raises():
    with pytest.raises(NotFoundError):
        await summary_service.generate("missing", "u1")


@pytest.mark.asyncio
async def test_generate_no_chunks_returns_placeholder():
    doc = FileModel.doc("u1", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    result = await summary_service.generate(fid, "u1")
    assert "no extracted content" in result["content"].lower()


@pytest.mark.asyncio
async def test_generate_with_chunks():
    doc = FileModel.doc("u1", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert(
        "u1",
        fid,
        [[0.1] * 768, [0.2] * 768],
        ["chunk one text", "chunk two text"],
        [{"page": 1}, {"page": 2}],
    )
    result = await summary_service.generate(fid, "u1")
    assert "FAKE SUMMARY" in result["content"]


@pytest.mark.asyncio
async def test_get_or_generate_uses_cache():
    doc = FileModel.doc("u1", "x.pdf", "x.pdf", "pdf", "k", 10)
    fid = await FileModel.insert(doc)
    await vector_store.upsert("u1", fid, [[0.1] * 768], ["only chunk"], [{}])

    r1 = await summary_service.get_or_generate(fid, "u1")
    r2 = await summary_service.get_or_generate(fid, "u1")
    assert r1["content"] == r2["content"]
