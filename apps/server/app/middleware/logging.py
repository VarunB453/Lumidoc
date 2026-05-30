"""Structured request/response logging."""
from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("http")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        client_ip = request.client.host if request.client else "-"
        method = request.method
        path = request.url.path
        try:
            response = await call_next(request)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            logger.exception(
                "request_failed",
                method=method,
                path=path,
                client_ip=client_ip,
                elapsed_ms=round(elapsed_ms, 2),
                error=str(e),
            )
            raise
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        logger.info(
            "request_completed",
            method=method,
            path=path,
            status_code=response.status_code,
            client_ip=client_ip,
            elapsed_ms=round(elapsed_ms, 2),
        )
        response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.2f}"
        return response
