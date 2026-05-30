"""Celery task: generate topic timestamps asynchronously."""
from __future__ import annotations

from typing import Any

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from app.core.logging import get_logger
from app.services.timestamp_service import timestamp_service
from app.tasks._runner import run_async, with_db_and_redis

logger = get_logger("task.timestamps")


async def _process(file_id: str, user_id: str) -> dict[str, Any]:
    entries = await timestamp_service.generate(file_id, user_id)
    return {"file_id": file_id, "status": "ready", "count": len(entries)}


@shared_task(
    bind=True,
    name="app.tasks.generate_timestamps.generate_timestamps",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def generate_timestamps(self, file_id: str, user_id: str) -> dict[str, Any]:
    try:
        return run_async(with_db_and_redis, _process, file_id, user_id)
    except Exception as e:
        logger.exception("timestamps_task_failed", file_id=file_id, error=str(e))
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            return {"file_id": file_id, "status": "failed", "error": str(e)}
