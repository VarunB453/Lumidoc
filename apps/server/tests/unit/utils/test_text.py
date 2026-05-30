"""Unit tests for app.utils.text helpers."""
from __future__ import annotations

import pytest

from app.utils import text as text_utils


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  hello   world  ", "hello world"),
        ("line1\n\nline2\t tab", "line1 line2 tab"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_whitespace(raw, expected):
    assert text_utils.normalize_whitespace(raw) == expected


def test_truncate_short_text_unchanged():
    assert text_utils.truncate("short", 10) == "short"


def test_truncate_long_text_appends_suffix():
    out = text_utils.truncate("abcdefghij", 5)
    assert out.endswith("…")
    assert len(out) == 5


def test_truncate_none():
    assert text_utils.truncate(None, 5) == ""


@pytest.mark.parametrize(
    "seconds,expected",
    [
        (0, "0:00"),
        (5, "0:05"),
        (83, "1:23"),
        (3600, "1:00:00"),
        (3725, "1:02:05"),
        (-3, "0:00"),
    ],
)
def test_format_seconds_hms(seconds, expected):
    assert text_utils.format_seconds_hms(seconds) == expected
