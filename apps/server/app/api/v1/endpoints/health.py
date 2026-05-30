"""Health check endpoints: /health, /ready, /live."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import settings
from app.core.logging import get_logger
from app.db.mongodb import MongoDB
from app.db.redis_client import RedisClient
from app.schemas.common import HealthResponse

logger = get_logger("health")

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Basic health check — always returns 200 if the process is alive."""
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        timestamp=datetime.now(UTC),
    )


@router.get("/ready")
async def readiness() -> dict:
    """Readiness probe — checks that DB and Redis are reachable."""
    checks: dict[str, str] = {}

    # MongoDB
    try:
        db = MongoDB.get_db()
        await db.command("ping")
        checks["mongodb"] = "ok"
    except Exception as e:
        checks["mongodb"] = f"error: {e}"

    # Redis
    try:
        client = RedisClient.get_client()
        await client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}


@router.get("/live")
async def liveness() -> dict:
    """Liveness probe — confirms the process is running."""
    return {"status": "alive", "timestamp": datetime.now(UTC).isoformat()}
