"""Script to create/ensure all MongoDB indexes.

Usage:
    python scripts/create_indexes.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.logging import get_logger
from app.db.indexes import ALL_INDEXES
from app.db.mongodb import MongoDB

logger = get_logger("create_indexes")


async def main() -> None:
    """Create all indexes defined in app.db.indexes."""
    logger.info("creating_indexes", env=settings.APP_ENV)
    await MongoDB.connect()
    try:
        db = MongoDB.get_db()
        for collection_name, indexes in ALL_INDEXES.items():
            await db[collection_name].create_indexes(indexes)
            logger.info("indexes_created", collection=collection_name, count=len(indexes))
        logger.info("all_indexes_created")
    finally:
        await MongoDB.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
