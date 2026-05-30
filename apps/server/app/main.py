"""FastAPI application entrypoint with middleware stack + lifespan."""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.mongodb import MongoDB, ensure_indexes
from app.db.redis_client import RedisClient
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.schemas.common import HealthResponse

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("app_starting", env=settings.APP_ENV, version=settings.APP_VERSION)
    await MongoDB.connect()
    try:
        await ensure_indexes()
    except Exception as e:  # pragma: no cover
        logger.warning("indexes_ensure_failed", error=str(e))
    await RedisClient.connect()
    yield
    logger.info("app_shutting_down")
    await RedisClient.disconnect()
    await MongoDB.disconnect()


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered document and media chat backend.",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ----- Middleware (ORDER MATTERS: outermost registered LAST runs FIRST) -----
    # Starlette runs middleware in reverse registration order. We register so that
    # CORS is outermost, then TrustedHost, then RequestID, Logging, RateLimit, Auth.
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware, enabled=not settings.is_test)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    # Session middleware required for Authlib OAuth flow.
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts_list,
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time-ms"],
    )

    # ----- Exception handlers -----
    register_exception_handlers(app)

    # ----- Routes -----
    app.include_router(api_router)

    @app.get("/", tags=["meta"])
    async def root() -> dict:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        }

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok", version=settings.APP_VERSION, timestamp=datetime.utcnow()
        )

    return app


app = create_app()
