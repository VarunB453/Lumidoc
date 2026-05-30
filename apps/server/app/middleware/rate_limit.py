"""Sliding-window Redis-based rate limiter (per IP + per user)."""
from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.logging import get_logger
from app.db.redis_client import RedisClient

logger = get_logger("rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter using Redis sorted sets.

    Two windows are enforced:
        - per-IP: RATE_LIMIT_PER_IP requests / RATE_LIMIT_WINDOW_SECONDS
        - per-user (if authenticated): RATE_LIMIT_PER_USER requests / window
    """

    EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/"}

    def __init__(self, app, enabled: bool = True) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.ip_limit = settings.RATE_LIMIT_PER_IP
        self.user_limit = settings.RATE_LIMIT_PER_USER
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled or request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        try:
            redis = RedisClient.get_ratelimit()
        except RuntimeError:
            # Redis not initialized (e.g. unit tests without lifespan)
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        user_id = self._extract_user_id(request)

        # ---- IP window ----
        try:
            allowed_ip, remaining_ip = await self._check_window(
                redis, f"rl:ip:{client_ip}", self.ip_limit, self.window
            )
        except Exception as e:
            logger.warning("rate_limit_unavailable", error=str(e))
            return await call_next(request)
        if not allowed_ip:
            return self._rate_limited_response("Too many requests from this IP.")

        # ---- User window ----
        if user_id:
            allowed_user, remaining_user = await self._check_window(
                redis, f"rl:user:{user_id}", self.user_limit, self.window
            )
            if not allowed_user:
                return self._rate_limited_response("Too many requests for this user.")
        else:
            remaining_user = self.user_limit

        response = await call_next(request)
        response.headers["X-RateLimit-Limit-IP"] = str(self.ip_limit)
        response.headers["X-RateLimit-Remaining-IP"] = str(remaining_ip)
        response.headers["X-RateLimit-Limit-User"] = str(self.user_limit)
        response.headers["X-RateLimit-Remaining-User"] = str(remaining_user)
        return response

    @staticmethod
    def _extract_user_id(request: Request) -> str | None:
        # AuthMiddleware (runs after this) sets request.state.user, so peek into the
        # Authorization header to make IDs stable.
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            return auth.split()[-1][:32]
        return None

    async def _check_window(
        self, redis, key: str, limit: int, window: int
    ) -> tuple[bool, int]:
        now = time.time()
        window_start = now - window
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {f"{now}:{id(self)}": now})
        pipe.zcard(key)
        pipe.expire(key, window + 1)
        _, _, count, _ = await pipe.execute()
        remaining = max(0, limit - int(count))
        allowed = int(count) <= limit
        return allowed, remaining

    @staticmethod
    def _rate_limited_response(message: str) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"error": {"code": "rate_limited", "message": message, "details": None}},
            headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
        )
