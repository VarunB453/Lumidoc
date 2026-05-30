"""Unit tests for Redis helper utilities (using fakeredis)."""
from __future__ import annotations

import pytest

from app.db.redis_client import (
    blacklist_token,
    cache_delete,
    cache_exists,
    cache_get,
    cache_get_json,
    cache_set,
    cache_set_json,
    clear_session,
    get_session,
    is_blacklisted,
    store_session,
)


@pytest.mark.asyncio
async def test_cache_set_get_delete():
    await cache_set("k1", "v1", ttl=60)
    assert await cache_get("k1") == "v1"
    assert await cache_exists("k1") is True
    await cache_delete("k1")
    assert await cache_get("k1") is None


@pytest.mark.asyncio
async def test_cache_set_without_ttl():
    await cache_set("k2", "v2")
    assert await cache_get("k2") == "v2"


@pytest.mark.asyncio
async def test_cache_json_roundtrip():
    await cache_set_json("j1", {"a": 1, "b": [1, 2]}, ttl=30)
    out = await cache_get_json("j1")
    assert out == {"a": 1, "b": [1, 2]}


@pytest.mark.asyncio
async def test_cache_get_json_missing():
    assert await cache_get_json("missing-json") is None


@pytest.mark.asyncio
async def test_cache_get_json_bad_json():
    await cache_set("bad-json", "not json")
    assert await cache_get_json("bad-json") is None


@pytest.mark.asyncio
async def test_blacklist_and_check():
    await blacklist_token("jti-1", 60)
    assert await is_blacklisted("jti-1") is True
    assert await is_blacklisted("other") is False


@pytest.mark.asyncio
async def test_blacklist_zero_ttl_noop():
    await blacklist_token("zero", 0)
    assert await is_blacklisted("zero") is False


@pytest.mark.asyncio
async def test_session_helpers():
    await store_session("u1", "jti-x", 60)
    assert await get_session("u1") == "jti-x"
    await clear_session("u1")
    assert await get_session("u1") is None
