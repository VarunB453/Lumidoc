"""Celery application factory."""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "lumidoc",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.process_pdf",
        "app.tasks.process_audio",
        "app.tasks.process_video",
        "app.tasks.generate_summary",
        "app.tasks.generate_timestamps",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.process_pdf.*": {"queue": "pdf"},
        "app.tasks.process_audio.*": {"queue": "audio"},
        "app.tasks.process_video.*": {"queue": "video"},
        "app.tasks.generate_summary.*": {"queue": "summary"},
        "app.tasks.generate_timestamps.*": {"queue": "timestamps"},
    },
    task_default_queue="default",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
)
