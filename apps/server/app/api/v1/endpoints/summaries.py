"""Summary endpoints: trigger + retrieve cached summaries."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.middleware.auth import get_current_user_id
from app.models.file import FileModel
from app.schemas.summary import SummaryResponse, SummaryStatusResponse
from app.services.summary_service import summary_service

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post(
    "/{file_id}",
    response_model=SummaryStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_summary(
    file_id: str, user_id: str = Depends(get_current_user_id)
) -> SummaryStatusResponse:
    # Verify ownership.
    doc = await FileModel.find_by_id(file_id, user_id)
    if not doc:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("File not found.")

    task_id: str | None = None
    try:
        from app.tasks.generate_summary import generate_summary

        res = generate_summary.delay(file_id, user_id)
        task_id = getattr(res, "id", None)
    except Exception:
        # Fallback: run inline.
        await summary_service.generate(file_id, user_id)

    return SummaryStatusResponse(
        file_id=file_id,
        status="processing" if task_id else "ready",
        task_id=task_id,
        message="Summary generation queued." if task_id else "Summary generated.",
    )


@router.get("/{file_id}", response_model=SummaryResponse)
async def get_summary(
    file_id: str, user_id: str = Depends(get_current_user_id)
) -> SummaryResponse:
    # Validate ownership.
    doc = await FileModel.find_by_id(file_id, user_id)
    if not doc:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("File not found.")
    summary = await summary_service.get_or_generate(file_id, user_id)
    return SummaryResponse.model_validate(summary)
