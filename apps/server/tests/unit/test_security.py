"""Unit tests for password hashing + JWT helpers."""
from __future__ import annotations

import time

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_remaining_seconds,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    h = hash_password("S3curePass!")
    assert h != "S3curePass!"
    assert verify_password("S3curePass!", h)
    assert not verify_password("wrong", h)


def test_password_verify_bad_hash_returns_false():
    assert verify_password("anything", "not-a-real-hash") is False


def test_access_token_roundtrip():
    tok = create_access_token("user-123", extra={"email": "u@example.com"})
    payload = decode_token(tok, expected_type="access")
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert payload["email"] == "u@example.com"


def test_refresh_token_returns_jti():
    tok, jti = create_refresh_token("u-1")
    assert jti
    payload = decode_token(tok, expected_type="refresh")
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"


def test_decode_wrong_token_type_raises():
    tok = create_access_token("u-1")
    with pytest.raises(JWTError):
        decode_token(tok, expected_type="refresh")


def test_decode_invalid_token():
    with pytest.raises(JWTError):
        decode_token("not.a.jwt")


def test_remaining_seconds_positive():
    tok = create_access_token("u-1")
    payload = decode_token(tok, expected_type="access")
    assert get_token_remaining_seconds(payload) > 0


def test_remaining_seconds_negative_clamped():
    assert get_token_remaining_seconds({"exp": int(time.time()) - 100}) == 0


def test_missing_jwt_keys_fail_in_production(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setattr(settings, "JWT_PRIVATE_KEY_PATH", str(tmp_path / "missing-private.pem"))
    monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", str(tmp_path / "missing-public.pem"))

    with pytest.raises(RuntimeError):
        settings.load_jwt_keys()
