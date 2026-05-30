"""User authentication service: register, login, refresh, logout."""
from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_remaining_seconds,
    hash_password,
    verify_password,
)
from app.db.redis_client import (
    blacklist_token,
    clear_session,
    is_blacklisted,
    store_session,
)
from app.models.user import UserModel
from app.schemas.user import TokenPair, UserPublic, UserRegister

logger = get_logger("auth_service")


class AuthService:
    """All auth flows live here so endpoints stay thin."""

    # ---------- register ----------
    async def register(self, payload: UserRegister) -> tuple[UserPublic, TokenPair]:
        try:
            existing = await UserModel.find_by_email(payload.email)
            if existing:
                raise ConflictError("A user with this email already exists.")
            doc = UserModel.doc(
                email=payload.email,
                hashed_password=hash_password(payload.password),
                name=payload.name,
                provider="local",
            )
            user_id = await UserModel.insert(doc)
            fresh = await UserModel.find_by_id(user_id)
            if not fresh:
                raise ServiceUnavailableError("User creation failed.")
            public = UserPublic.model_validate(UserModel.to_public(fresh))
        except ConflictError:
            raise
        except Exception as exc:
            logger.exception("register_failed", error=str(exc))
            raise ServiceUnavailableError(
                "Authentication database is unavailable."
            ) from exc

        tokens = await self._issue_tokens(user_id, email=payload.email)
        logger.info("user_registered", user_id=user_id)
        return public, tokens

    # ---------- login ----------
    async def login(self, email: str, password: str) -> tuple[UserPublic, TokenPair]:
        try:
            user = await UserModel.find_by_email(email)
            if not user or not user.get("hashed_password"):
                raise UnauthorizedError("Invalid email or password.")
            if not verify_password(password, user["hashed_password"]):
                raise UnauthorizedError("Invalid email or password.")
            if not user.get("is_active", True):
                raise UnauthorizedError("Account is deactivated.")
            public = UserPublic.model_validate(UserModel.to_public(user))
        except UnauthorizedError:
            raise
        except Exception as exc:
            logger.exception("login_failed", error=str(exc))
            raise ServiceUnavailableError(
                "Authentication database is unavailable."
            ) from exc

        tokens = await self._issue_tokens(str(user["_id"]), email=user["email"])
        logger.info("user_logged_in", user_id=str(user["_id"]))
        return public, tokens

    # ---------- oauth (google) ----------
    async def oauth_login_or_create(
        self,
        email: str,
        name: str,
        avatar_url: str | None = None,
    ) -> tuple[UserPublic, TokenPair]:
        try:
            user = await UserModel.find_by_email(email)
            if not user:
                doc = UserModel.doc(
                    email=email,
                    hashed_password=None,
                    name=name,
                    avatar_url=avatar_url,
                    provider="google",
                )
                user_id = await UserModel.insert(doc)
                user = await UserModel.find_by_id(user_id)
                logger.info("oauth_user_created", user_id=user_id)
            else:
                user_id = str(user["_id"])
            if not user:
                raise ServiceUnavailableError("OAuth user creation failed.")
            public = UserPublic.model_validate(UserModel.to_public(user))
        except Exception as exc:
            logger.exception("oauth_login_failed", error=str(exc))
            raise ServiceUnavailableError("Authentication database is unavailable.") from exc

        tokens = await self._issue_tokens(user_id, email=email)
        return public, tokens

    # ---------- refresh ----------
    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except Exception as e:
            raise UnauthorizedError("Invalid refresh token.") from e

        jti = payload.get("jti", "")
        user_id = payload.get("sub", "")
        try:
            blacklisted = await is_blacklisted(jti)
        except Exception as exc:
            logger.warning("redis_unavailable_refresh_blacklist_check", error=str(exc))
            blacklisted = False
        if blacklisted:
            raise UnauthorizedError("Refresh token has been revoked.")

        # Rotation: blacklist old one, issue new pair.
        ttl_left = get_token_remaining_seconds(payload)
        try:
            await blacklist_token(jti, ttl_left)
        except Exception as exc:
            logger.warning("redis_unavailable_refresh_blacklist_write", error=str(exc))
        return await self._issue_tokens(user_id, email=payload.get("email", ""))

    # ---------- logout ----------
    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except Exception:
            return  # idempotent
        jti = payload.get("jti", "")
        user_id = payload.get("sub", "")
        ttl_left = get_token_remaining_seconds(payload)
        if jti:
            try:
                await blacklist_token(jti, max(ttl_left, 1))
            except Exception as exc:
                logger.warning("redis_unavailable_logout_blacklist_write", error=str(exc))
        if user_id:
            try:
                await clear_session(user_id)
            except Exception as exc:
                logger.warning("redis_unavailable_logout_session_clear", error=str(exc))
        logger.info("user_logged_out", user_id=user_id)

    # ---------- helpers ----------
    async def _issue_tokens(self, user_id: str, email: str = "") -> TokenPair:
        access = create_access_token(user_id, extra={"email": email})
        refresh, jti = create_refresh_token(user_id, extra={"email": email})
        try:
            await store_session(user_id, jti, settings.REFRESH_TOKEN_TTL_DAYS * 86400)
        except Exception as exc:
            logger.warning("redis_unavailable_session_store", user_id=user_id, error=str(exc))
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.ACCESS_TOKEN_TTL_MINUTES * 60,
        )


auth_service = AuthService()
