"""Unit tests for FileService."""
from __future__ import annotations

import io

import pytest
from fastapi import UploadFile

from app.core.exceptions import NotFoundError, ValidationError
from app.services.file_service import FileService, file_service


def _make_upload(filename: str, data: bytes, content_type: str = "application/pdf") -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(data), headers={"content-type": content_type})


@pytest.mark.asyncio
async def test_upload_pdf_success(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", str(tmp_path))
    upload = _make_upload("doc.pdf", b"%PDF-1.4\n...")
    info = await file_service.upload("u1", upload)
    assert info["file_id"]
    assert info["file_type"] == "pdf"


@pytest.mark.asyncio
async def test_upload_audio_success(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", str(tmp_path))
    upload = _make_upload("track.mp3", b"\xff\xfb fakedata", content_type="audio/mpeg")
    info = await file_service.upload("u1", upload)
    assert info["file_type"] == "audio"


@pytest.mark.asyncio
async def test_upload_video_success(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", str(tmp_path))
    upload = _make_upload("clip.mp4", b"\x00\x00\x00 ftypmp42", content_type="video/mp4")
    info = await file_service.upload("u1", upload)
    assert info["file_type"] == "video"


@pytest.mark.asyncio
async def test_upload_empty_rejected():
    upload = _make_upload("empty.pdf", b"")
    with pytest.raises(ValidationError):
        await file_service.upload("u1", upload)


@pytest.mark.asyncio
async def test_upload_unsupported_extension():
    upload = _make_upload("doc.xyz", b"data")
    with pytest.raises(ValidationError):
        await file_service.upload("u1", upload)


@pytest.mark.asyncio
async def test_upload_too_large(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 0)  # any non-empty fails
    upload = _make_upload("doc.pdf", b"abc")
    with pytest.raises(ValidationError):
        await file_service.upload("u1", upload)


@pytest.mark.asyncio
async def test_get_missing_raises():
    with pytest.raises(NotFoundError):
        await file_service.get("507f1f77bcf86cd799439011", "u1")


@pytest.mark.asyncio
async def test_delete_missing_raises():
    with pytest.raises(NotFoundError):
        await file_service.delete("507f1f77bcf86cd799439011", "u1")


@pytest.mark.asyncio
async def test_list_pagination():
    docs, total = await file_service.list("u_list", page=1, page_size=10)
    assert isinstance(docs, list)
    assert isinstance(total, int)


@pytest.mark.asyncio
async def test_upload_then_delete_then_download(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", str(tmp_path))
    upload = _make_upload("doc.pdf", b"%PDF-1.4 hello")
    info = await file_service.upload("u_d", upload)
    fid = info["file_id"]

    # Download URL works.
    url = await file_service.download_url(fid, "u_d")
    assert url

    await file_service.delete(fid, "u_d")
    with pytest.raises(NotFoundError):
        await file_service.get(fid, "u_d")


def test_classify_unknown_extension():
    svc = FileService()
    with pytest.raises(ValidationError):
        svc._classify("file.txt", "text/plain")
