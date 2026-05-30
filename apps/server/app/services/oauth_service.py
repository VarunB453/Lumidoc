"""Google OAuth2 integration via Authlib."""
from __future__ import annotations

from typing import Any

import httpx
from authlib.integrations.starlette_client import OAuth, OAuthError

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, UnauthorizedError
from app.core.logging import get_logger

logger = get_logger("oauth")

GOOGLE_DISCOVERY = "https://accounts.google.com/.well-known/openid-configuration"


class GoogleOAuth:
    """Thin wrapper around Authlib for Google OAuth2 login."""

    def __init__(self) -> None:
        self.oauth = OAuth()
        if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
            self.oauth.register(
                name="google",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                server_metadata_url=GOOGLE_DISCOVERY,
                client_kwargs={"scope": "openid email profile"},
            )

    @property
    def client(self):
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ExternalServiceError(
                "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
            )
        client = self.oauth.create_client("google")
        if client is None:
            raise ExternalServiceError("Google OAuth is not configured.")
        return client

    async def authorize_redirect(self, request, redirect_uri: str | None = None):
        uri = redirect_uri or settings.GOOGLE_REDIRECT_URI
        return await self.client.authorize_redirect(request, uri)

    async def parse_callback(self, request) -> dict[str, Any]:
        """Exchange code → userinfo dict: {email, name, picture}."""
        try:
            token = await self.client.authorize_access_token(request)
        except OAuthError as e:
            raise UnauthorizedError(f"Google OAuth failed: {e.error}") from e
        userinfo = token.get("userinfo")
        if not userinfo:
            try:
                resp = await self.client.get("userinfo", token=token)
                userinfo = resp.json()
            except Exception as e:
                raise ExternalServiceError(f"Failed to fetch Google userinfo: {e}") from e
        return {
            "email": userinfo.get("email"),
            "name": userinfo.get("name") or userinfo.get("given_name") or "User",
            "avatar_url": userinfo.get("picture"),
            "sub": userinfo.get("sub"),
        }


google_oauth = GoogleOAuth()


async def fetch_google_userinfo_by_access_token(access_token: str) -> dict[str, Any]:
    """Convenience helper used by tests / alternative flows."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if resp.status_code != 200:
        raise UnauthorizedError("Invalid Google access token.")
    return resp.json()
