"""Authentication endpoints: register, login, refresh, logout, Google OAuth."""
from __future__ import annotations

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from app.core.exceptions import ExternalServiceError
from app.schemas.common import MessageResponse
from app.schemas.user import (
    LogoutRequest,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.services.auth_service import auth_service
from app.services.oauth_service import google_oauth

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthResponse(UserPublic):
    """Returned on register/login containing user + tokens."""

    tokens: TokenPair


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister) -> dict:
    user, tokens = await auth_service.register(payload)
    return {"user": user.model_dump(), "tokens": tokens.model_dump()}


@router.post("/login")
async def login(payload: UserLogin) -> dict:
    user, tokens = await auth_service.login(payload.email, payload.password)
    return {"user": user.model_dump(), "tokens": tokens.model_dump()}


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest) -> TokenPair:
    return await auth_service.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(payload: LogoutRequest) -> MessageResponse:
    await auth_service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out.")


# ---------- Google OAuth ----------
@router.get("/google")
async def google_login(request: Request):
    try:
        return await google_oauth.authorize_redirect(request)
    except Exception as e:
        raise ExternalServiceError(f"Google OAuth init failed: {e}") from e


@router.get("/google/callback")
async def google_callback(request: Request):
    userinfo = await google_oauth.parse_callback(request)
    email = userinfo.get("email")
    if not email:
        raise ExternalServiceError("Google OAuth did not return an email address.")
    user, tokens = await auth_service.oauth_login_or_create(
        email=email,
        name=userinfo.get("name", "User"),
        avatar_url=userinfo.get("avatar_url"),
    )
    # Redirect back to the frontend with tokens in the URL fragment so the
    # browser does not send them to the server on subsequent navigations.
    from urllib.parse import urlencode

    from app.core.config import settings as _settings

    target = _settings.GOOGLE_FRONTEND_REDIRECT or _settings.FRONTEND_ORIGIN
    fragment = urlencode(
        {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
        }
    )
    return RedirectResponse(url=f"{target}#{fragment}")
