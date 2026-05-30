"""Structured logging with structlog."""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Configure structlog + stdlib logging for the whole app."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.LOG_JSON:
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Route stdlib logging through stderr at the same level.
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)
    root = logging.getLogger()
    # Clear pre-existing handlers (uvicorn re-adds its own)
    root.handlers = [handler]
    root.setLevel(log_level)

    # Tame noisy libraries.
    for noisy in (
        "httpx",
        "httpcore",
        "urllib3",
        "openai",
        "botocore",
        "boto3",
        "pymongo",
        "pymongo.command",
        "pymongo.connection",
        "pymongo.serverSelection",
        "motor",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound to a given name."""
    return structlog.get_logger(name)
