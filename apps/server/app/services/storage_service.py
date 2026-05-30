"""S3 storage service with local filesystem fallback."""
from __future__ import annotations

import asyncio
import os
import uuid
from pathlib import Path
from typing import BinaryIO

import aiofiles

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("storage")


class StorageService:
    """Abstraction over S3 (boto3) + local FS for dev."""

    def __init__(self) -> None:
        self.use_local = settings.USE_LOCAL_STORAGE
        self.bucket = settings.S3_BUCKET_NAME
        self.local_root = Path(settings.LOCAL_STORAGE_PATH)
        if self.use_local:
            self.local_root.mkdir(parents=True, exist_ok=True)
        self._s3_client = None  # lazy

    # ---------- internal ----------
    def _get_s3(self):
        if self._s3_client is None:
            import boto3

            self._s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
                region_name=settings.AWS_REGION,
            )
        return self._s3_client

    @staticmethod
    def build_key(user_id: str, original_name: str, file_type: str) -> str:
        suffix = Path(original_name).suffix.lower()
        return f"users/{user_id}/{file_type}/{uuid.uuid4().hex}{suffix}"

    # ---------- API ----------
    async def upload_bytes(self, key: str, data: bytes, content_type: str | None = None) -> str:
        """Upload an in-memory blob. Returns the stored object key."""
        if self.use_local:
            path = self.local_root / key
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, "wb") as f:
                await f.write(data)
            logger.info("local_upload", key=key, bytes=len(data))
            return key

        def _put() -> None:
            kwargs = {"Bucket": self.bucket, "Key": key, "Body": data}
            if content_type:
                kwargs["ContentType"] = content_type
            self._get_s3().put_object(**kwargs)

        await asyncio.to_thread(_put)
        logger.info("s3_upload", key=key, bytes=len(data))
        return key

    async def upload_fileobj(self, key: str, fileobj: BinaryIO, content_type: str | None = None) -> str:
        """Upload a readable binary stream without materializing it in memory."""
        if self.use_local:
            path = self.local_root / key
            path.parent.mkdir(parents=True, exist_ok=True)
            total = 0
            async with aiofiles.open(path, "wb") as f:
                while chunk := fileobj.read(1024 * 1024):
                    if not isinstance(chunk, (bytes, bytearray)):
                        raise TypeError("Expected bytes-like stream.")
                    total += len(chunk)
                    await f.write(chunk)
            logger.info("local_upload", key=key, bytes=total)
            return key

        def _upload() -> None:
            kwargs = {"ExtraArgs": {"ContentType": content_type}} if content_type else {}
            self._get_s3().upload_fileobj(fileobj, self.bucket, key, **kwargs)

        await asyncio.to_thread(_upload)
        logger.info("s3_upload_stream", key=key)
        return key

    async def download_to_path(self, key: str, dest_path: str | os.PathLike) -> str:
        """Download object to a local filesystem path. Returns dest path."""
        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self.use_local:
            src = self.local_root / key
            if not src.exists():
                raise FileNotFoundError(f"Object not found: {key}")
            async with aiofiles.open(src, "rb") as fsrc, aiofiles.open(dest, "wb") as fdst:
                await fdst.write(await fsrc.read())
            return str(dest)

        def _dl() -> None:
            self._get_s3().download_file(self.bucket, key, str(dest))

        await asyncio.to_thread(_dl)
        return str(dest)

    async def get_object_bytes(self, key: str) -> bytes:
        if self.use_local:
            path = self.local_root / key
            if not path.exists():
                raise FileNotFoundError(f"Object not found: {key}")
            async with aiofiles.open(path, "rb") as f:
                return await f.read()

        def _get() -> bytes:
            resp = self._get_s3().get_object(Bucket=self.bucket, Key=key)
            return resp["Body"].read()

        return await asyncio.to_thread(_get)

    async def delete(self, key: str) -> None:
        if self.use_local:
            path = self.local_root / key
            if path.exists():
                path.unlink()
            return

        def _del() -> None:
            self._get_s3().delete_object(Bucket=self.bucket, Key=key)

        await asyncio.to_thread(_del)

    async def presigned_url(self, key: str, ttl: int | None = None) -> str:
        """Generate a presigned download URL. Falls back to a local route in dev."""
        ttl = ttl or settings.S3_PRESIGNED_URL_TTL
        if self.use_local:
            return f"/api/v1/local-files/{key}"

        def _sign() -> str:
            return self._get_s3().generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=ttl,
            )

        return await asyncio.to_thread(_sign)


storage_service = StorageService()
