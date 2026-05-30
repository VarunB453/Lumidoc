"""Application startup and shutdown event handlers."""
from __future__ import annotations

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.mongodb import MongoDB, ensure_indexes
from app.db.redis_client import RedisClient

logger = get_logger("events")


async def on_startup() -> None:
    """Run on application startup."""
    configure_logging()
    logger.info("app_starting", env=settings.APP_ENV, version=settings.APP_VERSION)

    # Connect to databases
    await MongoDB.connect()

    # Ensure indexes exist
    try:
        await ensure_indexes()
    except Exception as e:
        logger.warning("indexes_ensure_failed", error=str(e))

    # Connect to Redis
    await RedisClient.connect()

    logger.info("app_started_successfully")


async def on_shutdown() -> None:
    """Run on application shutdown."""
    logger.info("app_shutting_down")
    await RedisClient.disconnect()
    await MongoDB.disconnect()
    logger.info("app_shutdown_complete")
