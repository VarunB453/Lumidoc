"""Global error handler middleware for unhandled exceptions."""
from __future__ import annotations

import traceback

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("error_handler")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and return a structured JSON error response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                "unhandled_exception",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(exc),
                traceback=traceback.format_exc(),
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "An internal server error occurred.",
                    "request_id": request_id,
                },
            )
