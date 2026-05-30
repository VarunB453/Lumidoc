"""Unit tests for Settings + ephemeral key generation."""
from __future__ import annotations

from app.core.config import Settings, get_settings, settings


def test_settings_singleton():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_allowed_hosts_list():
    s = Settings(ALLOWED_HOSTS="a.com, b.com ,c.com")
    assert s.allowed_hosts_list == ["a.com", "b.com", "c.com"]


def test_allowed_hosts_empty_fallback():
    s = Settings(ALLOWED_HOSTS="")
    assert s.allowed_hosts_list == ["localhost"]


def test_cors_origins_dev_includes_localhost():
    s = Settings(APP_ENV="development", FRONTEND_ORIGIN="https://app.example.com")
    origins = s.cors_origins
    assert "https://app.example.com" in origins
    assert "http://localhost:3000" in origins


def test_is_production_flag():
    assert Settings(APP_ENV="production").is_production is True
    assert Settings(APP_ENV="development").is_production is False


def test_load_jwt_keys_returns_strings():
    priv, pub = settings.load_jwt_keys()
    assert "PRIVATE KEY" in priv
    assert "PUBLIC KEY" in pub


def test_is_test_flag():
    assert Settings(APP_ENV="test").is_test is True
