"""Unit tests for app.utils.validators helpers."""
from __future__ import annotations

import pytest
from bson import ObjectId

from app.utils import validators


@pytest.mark.parametrize(
    "email,valid",
    [
        ("alice@example.com", True),
        ("a.b+tag@sub.domain.io", True),
        ("  spaced@example.com  ", True),
        ("bad", False),
        ("bad@", False),
        ("bad@example", False),
    ],
)
def test_is_valid_email(email, valid):
    assert validators.is_valid_email(email) is valid


def test_is_valid_object_id():
    assert validators.is_valid_object_id(str(ObjectId())) is True
    assert validators.is_valid_object_id("not-an-id") is False


def test_is_strong_password_accepts_valid():
    ok, reason = validators.is_strong_password("Password1")
    assert ok is True
    assert reason == ""


@pytest.mark.parametrize(
    "password,fragment",
    [
        ("Aa1", "at least"),
        ("password1", "uppercase"),
        ("PASSWORD1", "lowercase"),
        ("Password", "digit"),
    ],
)
def test_is_strong_password_rejects_invalid(password, fragment):
    ok, reason = validators.is_strong_password(password)
    assert ok is False
    assert fragment in reason


def test_sanitize_string():
    assert validators.sanitize_string("  hi  ") == "hi"
    assert validators.sanitize_string("x" * 600, max_length=10) == "x" * 10


@pytest.mark.parametrize(
    "page,size,expected",
    [
        (1, 20, (1, 20)),
        (0, 0, (1, 1)),
        (-5, 999, (1, 100)),
        ("3", "50", (3, 50)),
        ("bad", "bad", (1, 20)),
        (None, None, (1, 20)),
    ],
)
def test_validate_pagination(page, size, expected):
    assert validators.validate_pagination(page, size) == expected
