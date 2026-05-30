"""FastAPI dependency injection helpers (Depends)."""
from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request, status

from app.core.logging import get_logger
from app.core.security import decode_token
from app.models.user import UserModel

logger = get_logger("dependencies")


async def get_current_user(request: Request) -> dict[str, Any]:
    """Extract and validate the current user from the Authorization header.

    Raises 401 if the token is missing, invalid, or the user doesn't exist.
    """
    auth_header: str | None = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header.",
        )

    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, expected_type="access")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim.",
        )

    user = await UserModel.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    return user


async def get_current_active_user(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Alias that ensures the user is active (already checked above)."""
    return user


async def require_admin(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Require the current user to have admin role."""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user


def get_pagination_params(
    page: int = 1,
    page_size: int = 20,
) -> dict[str, int]:
    """Common pagination query parameters."""
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    return {"skip": (page - 1) * page_size, "limit": page_size, "page": page}
