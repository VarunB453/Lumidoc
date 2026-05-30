"""Unit tests for app.utils.datetime helpers."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.utils import datetime as dt_utils


def test_utcnow_is_timezone_aware():
    now = dt_utils.utcnow()
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)


def test_to_iso_roundtrip():
    dt = datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC)
    iso = dt_utils.to_iso(dt)
    assert iso is not None
    assert dt_utils.from_iso(iso) == dt


def test_to_iso_none():
    assert dt_utils.to_iso(None) is None


def test_seconds_since_is_positive():
    past = dt_utils.utcnow() - timedelta(seconds=5)
    elapsed = dt_utils.seconds_since(past)
    assert elapsed >= 5.0


@pytest.mark.parametrize(
    "seconds,expected",
    [
        (-10, "0s"),
        (0, "0s"),
        (45, "45s"),
        (60, "1m 0s"),
        (125, "2m 5s"),
        (3600, "1h 0m 0s"),
        (3661, "1h 1m 1s"),
    ],
)
def test_format_duration(seconds, expected):
    assert dt_utils.format_duration(seconds) == expected
