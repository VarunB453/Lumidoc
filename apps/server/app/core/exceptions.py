"""Custom application exceptions + global handler."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger("exceptions")


class AppException(Exception):
    """Base class for all app-specific exceptions."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "An internal error occurred."

    def __init__(self, message: str | None = None, details: Any = None) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"
    message = "Resource not found."


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"
    message = "Authentication required."


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"
    message = "Access denied."


class ValidationError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "validation_error"
    message = "Invalid request data."


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"
    message = "Resource conflict."


class RateLimitError(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limited"
    message = "Too many requests."


class ServiceUnavailableError(AppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "service_unavailable"
    message = "Service temporarily unavailable."


class ExternalServiceError(AppException):
    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "external_service_error"
    message = "Upstream service error."


def register_exception_handlers(app: FastAPI) -> None:
    """Register global JSON exception handlers."""

    @app.exception_handler(AppException)
    async def _app_exc(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "app_exception",
            error_code=exc.error_code,
            message=exc.message,
            status=exc.status_code,
            path=str(request.url),
        )
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "http_error",
                    "message": exc.detail if isinstance(exc.detail, str) else "HTTP error",
                    "details": None,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def _val_exc(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", path=str(request.url), error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An internal error occurred.",
                    "details": None,
                }
            },
        )
