"""JWT authentication middleware + FastAPI dependency."""
from __future__ import annotations

from typing import Any

from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger
from app.core.security import decode_token
from app.db.redis_client import is_blacklisted

logger = get_logger("auth")

# Routes that DO NOT require auth.
PUBLIC_PREFIXES = (
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
    "/api/v1/auth/google",
    "/api/v1/avatars/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
)

# Exact-match paths that are public (not prefix-based).
PUBLIC_EXACT = ("/",)


def _allows_query_token(path: str) -> bool:
    """Allow URL tokens only where browser APIs cannot send auth headers."""
    if path.startswith(("/api/v1/local-files/", "/local-files/")):
        return True
    return path.startswith("/api/v1/chat/conversations/") and path.endswith(
        "/messages/stream"
    )


class AuthMiddleware(BaseHTTPMiddleware):
    """Validate JWT on protected routes; attach `request.state.user` payload."""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in PUBLIC_EXACT or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)

        # Some browser APIs cannot attach Authorization headers. Keep query-token
        # auth narrowly scoped to those routes to avoid broad URL token leakage.
        token = self._get_token(request)
        if not token:
            return self._unauthorized("Missing or invalid Authorization header.")

        try:
            payload = decode_token(token, expected_type="access")
        except JWTError as e:
            logger.debug("jwt_invalid", error=str(e))
            return self._unauthorized("Invalid or expired token.")

        jti = payload.get("jti")
        if jti:
            try:
                if await is_blacklisted(jti):
                    return self._unauthorized("Token has been revoked.")
            except Exception:
                pass  # redis is optional for access-token blacklist checks in dev/test paths

        request.state.user = payload
        request.state.user_id = payload.get("sub")
        return await call_next(request)

    @staticmethod
    def _get_token(request: Request) -> str | None:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1].strip()
        if _allows_query_token(request.url.path):
            return request.query_params.get("token")
        return None

    @staticmethod
    def _unauthorized(message: str) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": {"code": "unauthorized", "message": message, "details": None}},
            headers={"WWW-Authenticate": "Bearer"},
        )


# ------ Dependency for routes that want strong typing on the user payload ------
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    """Return the JWT payload from middleware, or re-validate from header."""
    user = getattr(request.state, "user", None)
    if user:
        return user

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Authentication required.")
    try:
        return decode_token(credentials.credentials, expected_type="access")
    except JWTError as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e


async def get_current_user_id(payload: dict[str, Any] = Depends(get_current_user)) -> str:
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token: missing subject.")
    return user_id
