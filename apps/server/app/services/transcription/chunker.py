"""Group Whisper segments into RAG-ready chunks while preserving timestamps."""
from __future__ import annotations

from typing import Any


def chunk_segments(
    segments: list[dict[str, Any]],
    target_chars: int = 800,
    overlap_chars: int = 100,
) -> list[dict[str, Any]]:
    """Group Whisper segments into ~target_chars chunks while preserving timestamps.

    Output: list of `{text, start_time, end_time}` dicts. Each chunk's
    `start_time` is the first source segment's start; `end_time` is the
    last source segment's end. `overlap_chars` of trailing segments are
    carried into the next chunk for retrieval continuity.
    """
    chunks: list[dict[str, Any]] = []
    buf: list[dict[str, Any]] = []
    buf_len = 0

    def flush() -> None:
        nonlocal buf, buf_len
        if not buf:
            return
        text = " ".join(s["text"] for s in buf).strip()
        chunks.append(
            {
                "text": text,
                "start_time": buf[0]["start"],
                "end_time": buf[-1]["end"],
            }
        )
        # Overlap: keep the trailing few segments for context.
        keep: list[dict[str, Any]] = []
        keep_len = 0
        for s in reversed(buf):
            if keep_len + len(s["text"]) > overlap_chars:
                break
            keep.insert(0, s)
            keep_len += len(s["text"]) + 1
        buf = keep
        buf_len = sum(len(s["text"]) + 1 for s in buf)

    for s in segments:
        text = (s.get("text") or "").strip()
        if not text:
            continue
        buf.append({"start": float(s["start"]), "end": float(s["end"]), "text": text})
        buf_len += len(text) + 1
        if buf_len >= target_chars:
            flush()
    flush()
    return chunks
