"""Celery Beat entrypoint for periodic task scheduling.

Usage:
    celery -A app.workers.celery_beat beat --loglevel=info
"""
from __future__ import annotations

from app.celery_app import celery_app
from app.tasks.schedules import BEAT_SCHEDULE

# Apply beat schedule
celery_app.conf.beat_schedule = BEAT_SCHEDULE
