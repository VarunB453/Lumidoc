"""Timestamp endpoints: trigger extraction, retrieve, search."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.middleware.auth import get_current_user_id
from app.models.file import FileModel
from app.schemas.timestamp import (
    TimestampEntry,
    TimestampListResponse,
    TimestampStatusResponse,
)
from app.services.timestamp_service import timestamp_service

router = APIRouter(prefix="/timestamps", tags=["timestamps"])


@router.post(
    "/{file_id}",
    response_model=TimestampStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_timestamps(
    file_id: str, user_id: str = Depends(get_current_user_id)
) -> TimestampStatusResponse:
    doc = await FileModel.find_by_id(file_id, user_id)
    if not doc:
        raise NotFoundError("File not found.")
    task_id: str | None = None
    try:
        from app.tasks.generate_timestamps import generate_timestamps

        res = generate_timestamps.delay(file_id, user_id)
        task_id = getattr(res, "id", None)
    except Exception:
        await timestamp_service.generate(file_id, user_id)
    return TimestampStatusResponse(
        file_id=file_id,
        status="processing" if task_id else "ready",
        task_id=task_id,
        message="Timestamp extraction queued." if task_id else "Timestamps generated.",
    )


@router.get("/{file_id}", response_model=TimestampListResponse)
async def get_timestamps(
    file_id: str, user_id: str = Depends(get_current_user_id)
) -> TimestampListResponse:
    doc = await FileModel.find_by_id(file_id, user_id)
    if not doc:
        raise NotFoundError("File not found.")
    entries = await timestamp_service.get_cached_or_generate(file_id, user_id)
    return TimestampListResponse(
        file_id=file_id,
        status="ready" if entries else "pending",
        entries=[TimestampEntry.model_validate(e) for e in entries],
    )


@router.get("/{file_id}/{topic}", response_model=TimestampListResponse)
async def search_timestamps(
    file_id: str,
    topic: str,
    user_id: str = Depends(get_current_user_id),
) -> TimestampListResponse:
    doc = await FileModel.find_by_id(file_id, user_id)
    if not doc:
        raise NotFoundError("File not found.")
    entries = await timestamp_service.search(file_id, topic)
    return TimestampListResponse(
        file_id=file_id,
        status="ready",
        entries=[TimestampEntry.model_validate(e) for e in entries],
    )
