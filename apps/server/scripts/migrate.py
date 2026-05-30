"""MongoDB migration runner.

Scans app/db/migrations/ for migration files and runs them in order.

Usage:
    python scripts/migrate.py
    python scripts/migrate.py --rollback
"""
from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.logging import get_logger
from app.db.mongodb import MongoDB

logger = get_logger("migrate")

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "app" / "db" / "migrations"


async def get_applied_migrations() -> set[str]:
    """Get the set of already-applied migration names from the DB."""
    db = MongoDB.get_db()
    collection = db["_migrations"]
    cursor = collection.find({}, {"name": 1})
    docs = await cursor.to_list(length=1000)
    return {doc["name"] for doc in docs}


async def record_migration(name: str) -> None:
    """Record a migration as applied."""
    from datetime import datetime, timezone

    db = MongoDB.get_db()
    await db["_migrations"].insert_one(
        {"name": name, "applied_at": datetime.now(timezone.utc)}
    )


async def run_migrations(rollback: bool = False) -> None:
    """Run pending migrations (or rollback the last one)."""
    migration_files = sorted(MIGRATIONS_DIR.glob("*.py"))
    migration_files = [f for f in migration_files if f.name != "__init__.py"]

    if not migration_files:
        logger.info("no_migrations_found")
        return

    applied = await get_applied_migrations()

    for mf in migration_files:
        name = mf.stem
        if rollback:
            # Only rollback the last applied migration
            continue

        if name in applied:
            logger.info("migration_already_applied", name=name)
            continue

        logger.info("applying_migration", name=name)
        spec = importlib.util.spec_from_file_location(name, mf)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "up"):
            await module.up()
            await record_migration(name)
            logger.info("migration_applied", name=name)
        else:
            logger.warning("migration_missing_up_function", name=name)


async def main() -> None:
    """Entrypoint."""
    rollback = "--rollback" in sys.argv
    logger.info("migration_runner_starting", env=settings.APP_ENV, rollback=rollback)
    await MongoDB.connect()
    try:
        await run_migrations(rollback=rollback)
        logger.info("migration_runner_complete")
    finally:
        await MongoDB.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
