"""Datetime utility helpers."""
from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(UTC)


def to_iso(dt: datetime | None) -> str | None:
    """Convert a datetime to ISO 8601 string, or None."""
    if dt is None:
        return None
    return dt.isoformat()


def from_iso(iso_str: str) -> datetime:
    """Parse an ISO 8601 string to a datetime."""
    return datetime.fromisoformat(iso_str)


def seconds_since(dt: datetime) -> float:
    """Return seconds elapsed since the given datetime."""
    return (utcnow() - dt).total_seconds()


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration string."""
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins}m {secs}s"
