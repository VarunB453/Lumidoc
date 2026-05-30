"""Unit tests for AuthService."""
from __future__ import annotations

import pytest

from app.core.exceptions import ConflictError, UnauthorizedError
from app.schemas.user import UserRegister
from app.services.auth_service import auth_service


@pytest.mark.asyncio
async def test_register_creates_user_and_tokens():
    payload = UserRegister(email="a@b.com", password="Password123", name="Alice")
    user, tokens = await auth_service.register(payload)
    assert user.email == "a@b.com"
    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.expires_in > 0


@pytest.mark.asyncio
async def test_register_duplicate_email_raises():
    payload = UserRegister(email="d@b.com", password="Password123", name="Dup")
    await auth_service.register(payload)
    with pytest.raises(ConflictError):
        await auth_service.register(payload)


@pytest.mark.asyncio
async def test_login_success():
    payload = UserRegister(email="l@b.com", password="Password123", name="L")
    await auth_service.register(payload)
    user, tokens = await auth_service.login("l@b.com", "Password123")
    assert user.email == "l@b.com"
    assert tokens.access_token


@pytest.mark.asyncio
async def test_login_wrong_password():
    payload = UserRegister(email="wp@b.com", password="Password123", name="WP")
    await auth_service.register(payload)
    with pytest.raises(UnauthorizedError):
        await auth_service.login("wp@b.com", "wrong")


@pytest.mark.asyncio
async def test_login_unknown_email():
    with pytest.raises(UnauthorizedError):
        await auth_service.login("nope@b.com", "anything")


@pytest.mark.asyncio
async def test_refresh_rotates_tokens():
    payload = UserRegister(email="r@b.com", password="Password123", name="R")
    _, tokens = await auth_service.register(payload)
    new_tokens = await auth_service.refresh(tokens.refresh_token)
    assert new_tokens.access_token
    assert new_tokens.refresh_token != tokens.refresh_token
    # Old refresh now blacklisted
    with pytest.raises(UnauthorizedError):
        await auth_service.refresh(tokens.refresh_token)


@pytest.mark.asyncio
async def test_refresh_invalid_token():
    with pytest.raises(UnauthorizedError):
        await auth_service.refresh("not.a.real.token")


@pytest.mark.asyncio
async def test_logout_blacklists_refresh():
    payload = UserRegister(email="lo@b.com", password="Password123", name="LO")
    _, tokens = await auth_service.register(payload)
    await auth_service.logout(tokens.refresh_token)
    with pytest.raises(UnauthorizedError):
        await auth_service.refresh(tokens.refresh_token)


@pytest.mark.asyncio
async def test_logout_is_idempotent_with_garbage():
    # Should silently swallow.
    await auth_service.logout("invalid.token.here")


@pytest.mark.asyncio
async def test_oauth_login_creates_user():
    user, tokens = await auth_service.oauth_login_or_create(
        email="oauth@b.com", name="OAuth", avatar_url="http://x/a.png"
    )
    assert user.email == "oauth@b.com"
    assert tokens.access_token


@pytest.mark.asyncio
async def test_oauth_login_existing_user():
    await auth_service.oauth_login_or_create(email="ex@b.com", name="Ex")
    user, _ = await auth_service.oauth_login_or_create(email="ex@b.com", name="Ex")
    assert user.email == "ex@b.com"
