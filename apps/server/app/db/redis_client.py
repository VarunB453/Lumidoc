"""Async Redis client wrappers (general cache + rate-limit + blacklist)."""
from __future__ import annotations

from typing import Any

import redis.asyncio as redis_async

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("redis")


class RedisClient:
    """Singleton holder for async Redis clients."""

    cache: redis_async.Redis | None = None
    ratelimit: redis_async.Redis | None = None
    available: bool = False

    @classmethod
    async def connect(cls) -> None:
        if cls.cache is not None:
            return
        cls.cache = redis_async.from_url(
            settings.REDIS_URL, decode_responses=True, encoding="utf-8"
        )
        cls.ratelimit = redis_async.from_url(
            settings.REDIS_URL, decode_responses=True, encoding="utf-8"
        )
        try:
            await cls.cache.ping()
            cls.available = True
            logger.info("redis_connected")
        except Exception as e:  # pragma: no cover
            cls.available = False
            logger.error("redis_ping_failed", error=str(e))

    @classmethod
    async def disconnect(cls) -> None:
        for c in (cls.cache, cls.ratelimit):
            if c is not None:
                await c.close()
        cls.cache = None
        cls.ratelimit = None
        cls.available = False
        logger.info("redis_disconnected")

    @classmethod
    def get_cache(cls) -> redis_async.Redis:
        if cls.cache is None or not cls.available:
            raise RuntimeError("Redis not initialized. Call RedisClient.connect() first.")
        return cls.cache

    @classmethod
    def get_ratelimit(cls) -> redis_async.Redis:
        if cls.ratelimit is None or not cls.available:
            raise RuntimeError("Redis not initialized. Call RedisClient.connect() first.")
        return cls.ratelimit

    @classmethod
    def optional_cache(cls) -> redis_async.Redis | None:
        """Return the cache client, or None when Redis is unavailable.

        Caching is a non-critical optimization, so callers using this helper
        degrade gracefully (cache miss / no-op) instead of failing the request
        when Redis is down — mirroring the rate limiter's behavior.
        """
        if cls.cache is None or not cls.available:
            return None
        return cls.cache


# -------- cache helpers (degrade gracefully when Redis is unavailable) --------
async def cache_get(key: str) -> str | None:
    client = RedisClient.optional_cache()
    if client is None:
        return None
    return await client.get(key)


async def cache_set(key: str, value: str, ttl: int | None = None) -> None:
    client = RedisClient.optional_cache()
    if client is None:
        return
    if ttl:
        await client.set(key, value, ex=ttl)
    else:
        await client.set(key, value)


async def cache_delete(key: str) -> None:
    client = RedisClient.optional_cache()
    if client is None:
        return
    await client.delete(key)


async def cache_exists(key: str) -> bool:
    client = RedisClient.optional_cache()
    if client is None:
        return False
    return bool(await client.exists(key))


# -------- blacklist --------
async def blacklist_token(jti: str, ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        return
    await RedisClient.get_cache().set(f"blacklist:{jti}", "1", ex=ttl_seconds)


async def is_blacklisted(jti: str) -> bool:
    return bool(await RedisClient.get_cache().exists(f"blacklist:{jti}"))


# -------- session --------
async def store_session(user_id: str, refresh_jti: str, ttl_seconds: int) -> None:
    await RedisClient.get_cache().set(f"session:{user_id}", refresh_jti, ex=ttl_seconds)


async def get_session(user_id: str) -> str | None:
    return await RedisClient.get_cache().get(f"session:{user_id}")


async def clear_session(user_id: str) -> None:
    await RedisClient.get_cache().delete(f"session:{user_id}")


# -------- generic JSON cache for services --------
import json


async def cache_get_json(key: str) -> Any | None:
    raw = await cache_get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def cache_set_json(key: str, value: Any, ttl: int | None = None) -> None:
    await cache_set(key, json.dumps(value, default=str), ttl=ttl)
