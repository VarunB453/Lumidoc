"""Inject an X-Request-ID header for every request (auto-generated if missing)."""
from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    HEADER = "X-Request-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        rid = request.headers.get(self.HEADER) or uuid.uuid4().hex
        request.state.request_id = rid
        structlog.contextvars.bind_contextvars(request_id=rid)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.unbind_contextvars("request_id")
        response.headers[self.HEADER] = rid
        return response
