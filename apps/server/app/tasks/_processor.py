"""Generic Celery wrapper for `process_<file_type>` tasks.

Eliminates ~80% of duplicated retry / error-handling / `_mark_failed`
boilerplate across `process_pdf`, `process_audio`, `process_video`.

Usage:
    @celery_processor("app.tasks.process_pdf.process_pdf", logger_name="task.pdf")
    async def _process(file_id: str, user_id: str) -> dict:
        ...
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from app.core.logging import get_logger
from app.models.file import FileModel
from app.tasks._runner import run_async, with_db_and_redis

ProcessFn = Callable[[str, str], Awaitable[dict[str, Any]]]


async def _mark_failed(file_id: str, message: str) -> None:
    await FileModel.update_status(file_id, "failed", error_message=message[:500])


def celery_processor(
    task_name: str, *, logger_name: str
) -> Callable[[ProcessFn], Any]:
    """Wrap an async `(file_id, user_id) -> dict` processor as a Celery task.

    Adds:
        - bind=True with retry: 3 attempts, exponential backoff (cap 600s, jitter)
        - DB + Redis bootstrap via `with_db_and_redis`
        - structured exception logging
        - best-effort `_mark_failed` to update file status on terminal failure
    """
    log = get_logger(logger_name)

    def decorator(process_fn: ProcessFn):
        @shared_task(
            bind=True,
            name=task_name,
            max_retries=3,
            autoretry_for=(Exception,),
            retry_backoff=True,
            retry_backoff_max=600,
            retry_jitter=True,
        )
        def _task(self, file_id: str, user_id: str) -> dict[str, Any]:
            try:
                return run_async(with_db_and_redis, process_fn, file_id, user_id)
            except Exception as e:
                log.exception(f"{logger_name}_failed", file_id=file_id, error=str(e))
                try:
                    run_async(with_db_and_redis, _mark_failed, file_id, str(e))
                except Exception:
                    pass
                try:
                    raise self.retry(exc=e)
                except MaxRetriesExceededError:
                    return {"file_id": file_id, "status": "failed", "error": str(e)}

        return _task

    return decorator
