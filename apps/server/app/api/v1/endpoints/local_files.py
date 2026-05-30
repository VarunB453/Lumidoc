"""Authenticated local-storage download route used in dev when USE_LOCAL_STORAGE=true.

Presigned-URL paths from `storage_service.presigned_url` look like
    /local-files/<key...>
This endpoint streams the file from disk. Access is controlled by the auth
middleware, so callers must provide a Bearer token (or `?token=` for browser
elements that cannot send headers, like <img> / <audio> / <video>).

Avatars are served from a public sibling route since they need to be embedded
via plain <img src> tags.
"""
from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.middleware.auth import get_current_user_id
from app.models.file import FileModel

router = APIRouter(prefix="/local-files", tags=["local-files"])


def _resolve(key: str) -> Path:
    if not settings.USE_LOCAL_STORAGE:
        raise NotFoundError("Local file route is disabled.")
    root = Path(settings.LOCAL_STORAGE_PATH).resolve()
    target = (root / key).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise NotFoundError("Invalid path.") from exc
    if not target.exists() or not target.is_file():
        raise NotFoundError("File not found.")
    return target


async def _authorize_key(key: str, user_id: str) -> None:
    doc = await FileModel.find_by_s3_key(key, user_id)
    if not doc:
        raise NotFoundError("Invalid path.")


@router.get("/{key:path}")
async def download_local_file(
    key: str, user_id: str = Depends(get_current_user_id)
):
    """Auth is enforced by AuthMiddleware (Bearer header OR ?token=)."""
    await _authorize_key(key, user_id)
    target = _resolve(key)
    media_type, _ = mimetypes.guess_type(target.name)
    return FileResponse(
        path=str(target),
        media_type=media_type or "application/octet-stream",
        filename=target.name,
    )
