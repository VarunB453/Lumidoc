"""Unit tests for user-related Pydantic schemas."""
from __future__ import annotations

from datetime import UTC

import pytest
from pydantic import ValidationError

from app.schemas.user import (
    PasswordChange,
    RefreshRequest,
    UserLogin,
    UserPublic,
    UserRegister,
)


def test_user_register_valid():
    u = UserRegister(email="alice@example.com", password="Password1", name="Alice")
    assert u.email == "alice@example.com"
    assert u.name == "Alice"


def test_user_register_rejects_weak_password():
    with pytest.raises(ValidationError) as exc:
        UserRegister(email="a@b.com", password="onlyletters", name="A")
    assert "letters and digits" in str(exc.value)


def test_user_register_rejects_short_password():
    with pytest.raises(ValidationError):
        UserRegister(email="a@b.com", password="Ab1", name="A")


def test_user_register_rejects_bad_email():
    with pytest.raises(ValidationError):
        UserRegister(email="not-an-email", password="Password1", name="A")


def test_user_login_minimal():
    login = UserLogin(email="a@b.com", password="x")
    assert login.password == "x"


def test_refresh_request_min_length():
    with pytest.raises(ValidationError):
        RefreshRequest(refresh_token="short")
    assert RefreshRequest(refresh_token="x" * 20).refresh_token == "x" * 20


def test_password_change_requires_long_new_password():
    with pytest.raises(ValidationError):
        PasswordChange(current_password="old", new_password="short")


def test_user_public_defaults():
    from datetime import datetime

    user = UserPublic(
        id="1",
        email="a@b.com",
        name="A",
        created_at=datetime.now(UTC),
    )
    assert user.role == "user"
    assert user.is_active is True
    assert user.avatar_url is None
