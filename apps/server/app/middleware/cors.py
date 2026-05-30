"""CORS middleware configuration helper.

The actual CORSMiddleware is added in main.py via FastAPI's add_middleware.
This module provides a helper to build CORS config from settings.
"""
from __future__ import annotations

from typing import Any

from app.core.config import settings


def get_cors_config() -> dict[str, Any]:
    """Return CORS configuration dict suitable for CORSMiddleware kwargs."""
    return {
        "allow_origins": settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": ["X-Request-ID", "X-Response-Time-ms"],
    }
