"""File upload + management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, UploadFile, status

from app.core.config import settings
from app.middleware.auth import get_current_user_id
from app.models.file import FileModel
from app.schemas.common import MessageResponse, Page, PaginationMeta
from app.schemas.file import FileDownloadURL, FileMetadata, FileUploadResponse
from app.services.file_service import file_service

router = APIRouter(prefix="/files", tags=["files"])


def _dispatch_processing(file_id: str, user_id: str, file_type: str) -> str | None:
    """Send the processing job to the appropriate Celery queue. Returns task_id."""
    try:
        if file_type == "pdf":
            from app.tasks.process_pdf import process_pdf

            res = process_pdf.delay(file_id, user_id)
        elif file_type == "audio":
            from app.tasks.process_audio import process_audio

            res = process_audio.delay(file_id, user_id)
        elif file_type == "video":
            from app.tasks.process_video import process_video

            res = process_video.delay(file_id, user_id)
        else:
            return None
        return getattr(res, "id", None)
    except Exception:
        # In dev (no broker) just return None.
        return None


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    user_id: str = Depends(get_current_user_id),
) -> FileUploadResponse:
    info = await file_service.upload(user_id, file)
    file_id = info["file_id"]
    task_id = _dispatch_processing(file_id, user_id, info["file_type"])
    doc = info["doc"]
    return FileUploadResponse(
        file_id=file_id,
        filename=doc["filename"],
        original_name=doc["original_name"],
        file_type=doc["file_type"],
        size_bytes=doc["size_bytes"],
        status=doc["status"],
        task_id=task_id,
    )


@router.get("", response_model=Page[FileMetadata])
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    user_id: str = Depends(get_current_user_id),
) -> Page[FileMetadata]:
    docs, total = await file_service.list(user_id, page, page_size, status_filter)
    items = [FileMetadata.model_validate(FileModel.to_public(d)) for d in docs]
    total_pages = (total + page_size - 1) // page_size
    return Page[FileMetadata](
        items=items,
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )


@router.get("/{file_id}", response_model=FileMetadata)
async def get_file(file_id: str, user_id: str = Depends(get_current_user_id)) -> FileMetadata:
    doc = await file_service.get(file_id, user_id)
    return FileMetadata.model_validate(FileModel.to_public(doc))


@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: str, user_id: str = Depends(get_current_user_id)
) -> MessageResponse:
    await file_service.delete(file_id, user_id)
    return MessageResponse(message="File deleted.")


@router.get("/{file_id}/download", response_model=FileDownloadURL)
async def download_file(
    file_id: str, user_id: str = Depends(get_current_user_id)
) -> FileDownloadURL:
    url = await file_service.download_url(file_id, user_id)
    return FileDownloadURL(file_id=file_id, url=url, expires_in=settings.S3_PRESIGNED_URL_TTL)
