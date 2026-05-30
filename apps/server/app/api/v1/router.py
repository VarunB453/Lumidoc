"""Aggregate API v1 router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    avatars,
    chat,
    files,
    health,
    local_files,
    misc,
    summaries,
    timestamps,
    users,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(files.router)
api_router.include_router(chat.router)
api_router.include_router(summaries.router)
api_router.include_router(timestamps.router)
api_router.include_router(misc.router)
api_router.include_router(local_files.router)
api_router.include_router(avatars.router)
api_router.include_router(health.router)
