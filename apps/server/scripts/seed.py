"""Seed script — populate the database with initial/sample data.

Usage:
    python scripts/seed.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.mongodb import MongoDB
from app.models.user import UserModel

logger = get_logger("seed")


async def seed_admin_user() -> None:
    """Create a default admin user if one doesn't exist."""
    admin_email = "admin@lumidoc.io"
    existing = await UserModel.find_by_email(admin_email)
    if existing:
        logger.info("admin_user_exists", email=admin_email)
        return

    doc = UserModel.doc(
        email=admin_email,
        hashed_password=hash_password("Admin123!"),
        name="Admin",
        role="admin",
        provider="local",
    )
    user_id = await UserModel.insert(doc)
    logger.info("admin_user_created", user_id=user_id, email=admin_email)


async def main() -> None:
    """Run all seed operations."""
    logger.info("seed_starting", env=settings.APP_ENV)
    await MongoDB.connect()
    try:
        await seed_admin_user()
        logger.info("seed_complete")
    finally:
        await MongoDB.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
