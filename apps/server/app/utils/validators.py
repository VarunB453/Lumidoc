"""Input validation utility helpers."""
from __future__ import annotations

import re
from typing import Any

from bson import ObjectId

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PASSWORD_MIN_LENGTH = 8


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email.strip()))


def is_valid_object_id(value: str) -> bool:
    """Check if a string is a valid MongoDB ObjectId."""
    try:
        ObjectId(value)
        return True
    except Exception:
        return False


def is_strong_password(password: str) -> tuple[bool, str]:
    """Check password strength. Returns (is_valid, reason)."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Strip and truncate a string input."""
    return value.strip()[:max_length]


def validate_pagination(page: Any, page_size: Any) -> tuple[int, int]:
    """Validate and normalize pagination parameters."""
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = max(1, min(100, int(page_size)))
    except (TypeError, ValueError):
        page_size = 20
    return page, page_size
