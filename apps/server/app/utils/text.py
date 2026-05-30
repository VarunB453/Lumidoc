"""Misc text utility helpers."""
from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def truncate(text: str, max_len: int, suffix: str = "…") -> str:
    if not text or len(text) <= max_len:
        return text or ""
    return text[: max(0, max_len - len(suffix))] + suffix


def format_seconds_hms(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"
