"""Unit tests for StorageService (local fallback)."""
from __future__ import annotations

import pytest

from app.services.storage_service import StorageService


@pytest.fixture
def store(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "USE_LOCAL_STORAGE", True)
    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", str(tmp_path))
    return StorageService()


@pytest.mark.asyncio
async def test_upload_and_download(store, tmp_path):
    key = store.build_key("u1", "doc.pdf", "pdf")
    assert key.startswith("users/u1/pdf/")
    await store.upload_bytes(key, b"hello", content_type="application/pdf")
    out = tmp_path / "out.pdf"
    await store.download_to_path(key, out)
    assert out.read_bytes() == b"hello"


@pytest.mark.asyncio
async def test_get_object_bytes(store):
    key = "test/x.bin"
    await store.upload_bytes(key, b"abc")
    data = await store.get_object_bytes(key)
    assert data == b"abc"


@pytest.mark.asyncio
async def test_get_object_bytes_missing(store):
    with pytest.raises(FileNotFoundError):
        await store.get_object_bytes("nope")


@pytest.mark.asyncio
async def test_download_missing(store, tmp_path):
    with pytest.raises(FileNotFoundError):
        await store.download_to_path("missing", tmp_path / "x")


@pytest.mark.asyncio
async def test_delete(store):
    key = "to/delete.bin"
    await store.upload_bytes(key, b"x")
    await store.delete(key)
    with pytest.raises(FileNotFoundError):
        await store.get_object_bytes(key)


@pytest.mark.asyncio
async def test_delete_missing_is_noop(store):
    # Should not raise
    await store.delete("not-there")


@pytest.mark.asyncio
async def test_presigned_url_local(store):
    url = await store.presigned_url("users/u/pdf/x.pdf")
    assert url.startswith("/api/v1/local-files/")


@pytest.mark.asyncio
async def test_upload_fileobj(store):
    import io

    fobj = io.BytesIO(b"abc")
    key = "x/y.bin"
    await store.upload_fileobj(key, fobj)
    assert await store.get_object_bytes(key) == b"abc"


def test_build_key_unique(store):
    a = store.build_key("u", "a.pdf", "pdf")
    b = store.build_key("u", "a.pdf", "pdf")
    assert a != b
