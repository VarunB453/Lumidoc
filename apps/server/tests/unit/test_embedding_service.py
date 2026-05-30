"""Unit tests for EmbeddingService (fake embed_texts in conftest)."""
from __future__ import annotations

import pytest

from app.services.embedding_service import EmbeddingService, embedding_service


@pytest.mark.asyncio
async def test_embed_texts_returns_vectors():
    vectors = await embedding_service.embed_texts(["hello", "world"])
    assert len(vectors) == 2
    assert all(len(v) == 768 for v in vectors)


@pytest.mark.asyncio
async def test_embed_texts_empty_returns_empty():
    assert await embedding_service.embed_texts([]) == []
    assert await embedding_service.embed_texts(["  ", ""]) == []


@pytest.mark.asyncio
async def test_embed_query_returns_single_vector():
    vec = await embedding_service.embed_query("question")
    assert isinstance(vec, list)
    assert len(vec) == 768


def test_embedding_service_batch_size_const():
    assert EmbeddingService.BATCH_SIZE == 100


@pytest.mark.asyncio
async def test_embed_texts_deduplicates_whitespace():
    vectors = await embedding_service.embed_texts(["   text  "])
    assert len(vectors) == 1
