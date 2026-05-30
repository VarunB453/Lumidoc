"""File upload + metadata service."""
from __future__ import annotations

import mimetypes
import tempfile
import uuid
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.file import FileModel
from app.services.storage_service import storage_service
from app.services.vector_store import vector_store

logger = get_logger("file_service")

ALLOWED_EXT = {
    ".pdf": "pdf",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
    ".ogg": "audio",
    ".mp4": "video",
    ".mov": "video",
    ".webm": "video",
    ".mkv": "video",
}

ALLOWED_MIME_PREFIX = {
    "pdf": {"application/pdf"},
    "audio": {"audio/"},
    "video": {"video/"},
}

UPLOAD_CHUNK_SIZE = 1024 * 1024


class FileService:
    """Validate + persist uploaded files."""

    def _detect_mime(self, data: bytes, filename: str) -> str:
        # Prefer python-magic if available, else fall back to extension.
        try:
            import magic

            return magic.from_buffer(data, mime=True) or ""
        except Exception:
            guess, _ = mimetypes.guess_type(filename)
            return guess or "application/octet-stream"

    def _classify(self, filename: str, mime: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            raise ValidationError(f"Unsupported extension: {ext}")
        file_type = ALLOWED_EXT[ext]
        accepted = ALLOWED_MIME_PREFIX[file_type]
        if not any(mime == m or mime.startswith(m) for m in accepted):
            # Don't be strict if magic returns generic types — fall back to extension.
            logger.warning("mime_mismatch", mime=mime, ext=ext, fallback="extension")
        return file_type

    async def _spool_upload(
        self, upload: UploadFile, max_bytes: int
    ) -> tuple[Path, int, bytes]:
        tmp = tempfile.NamedTemporaryFile(prefix="lumidoc-upload-", delete=False)
        tmp_path = Path(tmp.name)
        tmp.close()
        size = 0
        sample = b""
        try:
            async with aiofiles.open(tmp_path, "wb") as out:
                while chunk := await upload.read(UPLOAD_CHUNK_SIZE):
                    size += len(chunk)
                    if size > max_bytes:
                        raise ValidationError(
                            f"File too large ({size} bytes). Max {settings.MAX_UPLOAD_SIZE_MB} MB."
                        )
                    if len(sample) < UPLOAD_CHUNK_SIZE:
                        sample += chunk[: UPLOAD_CHUNK_SIZE - len(sample)]
                    await out.write(chunk)
            if size == 0:
                raise ValidationError("Empty file.")
            return tmp_path, size, sample
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise

    async def upload(self, user_id: str, upload: UploadFile) -> dict[str, Any]:
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        tmp_path, size, sample = await self._spool_upload(upload, max_bytes)

        try:
            original_name = upload.filename or f"upload-{uuid.uuid4().hex}"
            mime = self._detect_mime(sample, original_name)
            file_type = self._classify(original_name, mime)

            # 2. Build storage key, persist.
            key = storage_service.build_key(user_id, original_name, file_type)
            with tmp_path.open("rb") as fh:
                await storage_service.upload_fileobj(key, fh, content_type=mime)

            # 3. Insert file doc.
            doc = FileModel.doc(
                user_id=user_id,
                filename=Path(key).name,
                original_name=original_name,
                file_type=file_type,
                s3_key=key,
                size_bytes=size,
                mime_type=mime,
            )
            file_id = await FileModel.insert(doc)
            logger.info("file_uploaded", file_id=file_id, file_type=file_type, bytes=size)
            return {"file_id": file_id, "doc": doc, "file_type": file_type}
        finally:
            tmp_path.unlink(missing_ok=True)

    async def list(
        self, user_id: str, page: int, page_size: int, status: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        return await FileModel.list_for_user(user_id, page, page_size, status)

    async def get(self, file_id: str, user_id: str) -> dict[str, Any]:
        doc = await FileModel.find_by_id(file_id, user_id)
        if not doc:
            raise NotFoundError("File not found.")
        return doc

    async def delete(self, file_id: str, user_id: str) -> None:
        doc = await self.get(file_id, user_id)
        ok = await FileModel.soft_delete(file_id, user_id)
        if not ok:
            raise NotFoundError("File not found.")
        # Best-effort: remove the vector namespace.
        try:
            await vector_store.delete_namespace(user_id, file_id)
        except Exception as e:
            logger.warning("vector_delete_failed", file_id=file_id, error=str(e))

    async def download_url(self, file_id: str, user_id: str) -> str:
        doc = await self.get(file_id, user_id)
        return await storage_service.presigned_url(doc["s3_key"])


file_service = FileService()
