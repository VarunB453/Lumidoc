"""Celery worker entrypoint.

Usage:
    celery -A app.workers.celery_worker worker --loglevel=info --concurrency=4
"""
from __future__ import annotations

from app.celery_app import celery_app  # noqa: F401

# The celery_app import registers all tasks via the `include` config.
# This module serves as the worker entrypoint for deployment scripts.
