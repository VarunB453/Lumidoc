"""Security hardening regressions."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_query_token_is_rejected_on_regular_api_routes(client, auth_headers):
    token = auth_headers["Authorization"].split(" ", 1)[1]

    resp = await client.get(f"/api/v1/users/me?token={token}")

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_local_file_download_requires_owned_key(client, auth_headers):
    from app.core.config import settings
    from app.models.file import FileModel

    user_id = auth_headers["user"]["id"]
    key = f"users/{user_id}/pdf/owned.pdf"
    local_path = Path(settings.LOCAL_STORAGE_PATH) / key
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(b"%PDF-1.4 owned")

    doc = FileModel.doc(
        user_id=user_id,
        filename="owned.pdf",
        original_name="owned.pdf",
        file_type="pdf",
        s3_key=key,
        size_bytes=14,
        mime_type="application/pdf",
    )
    await FileModel.insert(doc)

    headers = {"Authorization": auth_headers["Authorization"]}

    owned = await client.get(f"/api/v1/local-files/{key}", headers=headers)
    assert owned.status_code == 200
    assert owned.content == b"%PDF-1.4 owned"

    other_key = "users/other-user/pdf/owned.pdf"
    other_path = Path(settings.LOCAL_STORAGE_PATH) / other_key
    other_path.parent.mkdir(parents=True, exist_ok=True)
    other_path.write_bytes(b"%PDF-1.4 other")

    denied = await client.get(f"/api/v1/local-files/{other_key}", headers=headers)
    assert denied.status_code == 404


@pytest.mark.asyncio
async def test_local_file_query_token_still_works_for_media_urls(client, auth_headers):
    from app.core.config import settings
    from app.models.file import FileModel

    user_id = auth_headers["user"]["id"]
    token = auth_headers["Authorization"].split(" ", 1)[1]
    key = f"users/{user_id}/audio/clip.mp3"
    local_path = Path(settings.LOCAL_STORAGE_PATH) / key
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(b"audio")

    doc = FileModel.doc(
        user_id=user_id,
        filename="clip.mp3",
        original_name="clip.mp3",
        file_type="audio",
        s3_key=key,
        size_bytes=5,
        mime_type="audio/mpeg",
    )
    await FileModel.insert(doc)

    resp = await client.get(f"/api/v1/local-files/{key}?token={token}")

    assert resp.status_code == 200
    assert resp.content == b"audio"
