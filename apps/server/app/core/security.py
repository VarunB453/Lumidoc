"""Password hashing + JWT token utilities (RS256)."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

TokenType = Literal["access", "refresh"]


# ---------- password ----------
def hash_password(password: str) -> str:
    """Bcrypt-hash a password (cost 12)."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against bcrypt hash."""
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False


# ---------- JWT ----------
def _now() -> datetime:
    return datetime.now(UTC)


def _build_claims(
    subject: str,
    token_type: TokenType,
    extra: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> dict[str, Any]:
    now = _now()
    if expires_delta is None:
        expires_delta = (
            timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES)
            if token_type == "access"
            else timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
        )
    claims: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "nbf": int(now.timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "jti": uuid.uuid4().hex,
        "type": token_type,
    }
    if extra:
        claims.update(extra)
    return claims


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    """Create a signed JWT access token."""
    private_key, _ = settings.load_jwt_keys()
    claims = _build_claims(subject, "access", extra)
    return jwt.encode(claims, private_key, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, str]:
    """Create a signed JWT refresh token. Returns (token, jti)."""
    private_key, _ = settings.load_jwt_keys()
    claims = _build_claims(subject, "refresh", extra)
    token = jwt.encode(claims, private_key, algorithm=settings.JWT_ALGORITHM)
    return token, claims["jti"]


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Decode + verify a JWT. Raises jose.JWTError on bad token."""
    _, public_key = settings.load_jwt_keys()
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[settings.JWT_ALGORITHM],
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
    )
    if expected_type and payload.get("type") != expected_type:
        raise JWTError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")
    return payload


def get_token_remaining_seconds(payload: dict[str, Any]) -> int:
    """Return how many seconds until token expiration (>=0)."""
    exp = int(payload.get("exp", 0))
    now = int(_now().timestamp())
    return max(0, exp - now)
