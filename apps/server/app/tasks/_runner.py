"""Shared helper to run async coroutines inside Celery tasks."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


def run_async(coro_fn: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
    """Run an async function from a synchronous Celery worker context.

    Builds a fresh event loop so we never share a loop across tasks.
    """
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro_fn(*args, **kwargs))
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()
        asyncio.set_event_loop(None)


async def with_db_and_redis(coro_fn: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
    """Ensure DB + Redis are connected for the duration of `coro_fn`."""
    from app.db.mongodb import MongoDB
    from app.db.redis_client import RedisClient

    await MongoDB.connect()
    await RedisClient.connect()
    try:
        return await coro_fn(*args, **kwargs)
    finally:
        # Keep connections alive for re-use within the worker process; only close on exit.
        pass
