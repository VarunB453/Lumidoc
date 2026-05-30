"""Publicly-readable avatar route (so <img src> works without auth header).

Avatars are intentionally low-sensitivity. Authentication is required to UPLOAD
them (see `users.py`); reading them is open. Avatars live under
`<storage>/users/<user_id>/avatar/<filename>`.
"""
from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/avatars", tags=["avatars"])


@router.get("/{user_id}/{filename}")
async def get_avatar(user_id: str, filename: str):
    if not settings.USE_LOCAL_STORAGE:
        raise NotFoundError("Avatar route is disabled.")
    root = Path(settings.LOCAL_STORAGE_PATH).resolve()
    target = (root / "users" / user_id / "avatar" / filename).resolve()
    if not str(target).startswith(str(root)):
        raise NotFoundError("Invalid path.")
    if not target.exists() or not target.is_file():
        raise NotFoundError("Avatar not found.")
    media_type, _ = mimetypes.guess_type(target.name)
    return FileResponse(
        path=str(target),
        media_type=media_type or "image/png",
        filename=target.name,
    )
