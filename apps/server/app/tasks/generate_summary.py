"""Celery task: generate file summary asynchronously."""
from __future__ import annotations

from typing import Any

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from app.core.logging import get_logger
from app.services.summary_service import summary_service
from app.tasks._runner import run_async, with_db_and_redis

logger = get_logger("task.summary")


async def _process(file_id: str, user_id: str) -> dict[str, Any]:
    result = await summary_service.generate(file_id, user_id)
    return {"file_id": file_id, "status": "ready", "summary_id": result.get("id")}


@shared_task(
    bind=True,
    name="app.tasks.generate_summary.generate_summary",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def generate_summary(self, file_id: str, user_id: str) -> dict[str, Any]:
    try:
        return run_async(with_db_and_redis, _process, file_id, user_id)
    except Exception as e:
        logger.exception("summary_task_failed", file_id=file_id, error=str(e))
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            return {"file_id": file_id, "status": "failed", "error": str(e)}
