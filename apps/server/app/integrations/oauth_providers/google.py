"""Google OAuth provider integration."""
from __future__ import annotations

from typing import Any

from authlib.integrations.starlette_client import OAuth

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("oauth_google")

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def get_google_user_info(token: dict[str, Any]) -> dict[str, Any]:
    """Extract user info from Google OAuth token response."""
    userinfo = token.get("userinfo", {})
    return {
        "email": userinfo.get("email", ""),
        "name": userinfo.get("name", ""),
        "avatar_url": userinfo.get("picture"),
        "provider": "google",
    }
