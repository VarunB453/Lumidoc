"""File-related Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import ORMModel

FileType = Literal["pdf", "audio", "video"]
FileStatus = Literal["pending", "processing", "ready", "failed"]


class FileMetadata(ORMModel):
    id: str
    user_id: str
    filename: str
    original_name: str
    file_type: FileType
    s3_key: str
    size_bytes: int = Field(..., ge=0)
    status: FileStatus
    error_message: str | None = None
    mime_type: str | None = None
    duration_seconds: float | None = None
    page_count: int | None = None
    created_at: datetime
    processed_at: datetime | None = None
    is_deleted: bool = False


class FileUploadResponse(ORMModel):
    file_id: str
    filename: str
    original_name: str
    file_type: FileType
    size_bytes: int
    status: FileStatus
    task_id: str | None = None


class FileDownloadURL(ORMModel):
    file_id: str
    url: str
    expires_in: int
