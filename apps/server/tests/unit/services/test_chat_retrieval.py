"""Unit tests for the pure helpers in app.services.chat.retrieval."""
from __future__ import annotations

from app.services.chat import retrieval


def test_extract_timestamp_refs_mm_ss_and_hh_mm_ss():
    refs = retrieval.extract_timestamp_refs("See at 02:30 and 01:15:45.")
    seconds = {r["seconds"] for r in refs}
    assert 150.0 in seconds  # 02:30
    assert 4545.0 in seconds  # 01:15:45


def test_extract_timestamp_refs_none():
    assert retrieval.extract_timestamp_refs("plain text without time") == []


def test_format_context_empty():
    assert "no relevant context" in retrieval.format_context([])


def test_format_context_includes_page_and_time():
    chunks = [
        {"text": "alpha", "page": 3},
        {"text": "beta", "start_time": 1.0, "end_time": 2.5},
    ]
    out = retrieval.format_context(chunks)
    assert "page 3" in out
    assert "1.0s" in out and "2.5s" in out
    assert "alpha" in out and "beta" in out


def test_format_history_empty():
    assert retrieval.format_history([]) == "(no prior messages)"


def test_format_history_renders_roles_uppercased():
    out = retrieval.format_history(
        [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "yo"}]
    )
    assert "USER: hi" in out
    assert "ASSISTANT: yo" in out


def test_chunks_to_meta_truncates_text():
    chunks = [{"file_id": "f", "chunk_id": "c", "text": "x" * 1000, "score": 0.9}]
    meta = retrieval.chunks_to_meta(chunks)
    assert len(meta[0]["text"]) == 600
    assert meta[0]["score"] == 0.9


def test_refs_to_meta_uses_first_file_id():
    refs = [{"seconds": 12.0}, {"seconds": 30.0}]
    meta = retrieval.refs_to_meta(refs, ["fileA", "fileB"])
    assert all(m["file_id"] == "fileA" for m in meta)
    assert meta[0]["start_time"] == 12.0
    assert meta[0]["topic"] is None


def test_refs_to_meta_empty_file_ids():
    meta = retrieval.refs_to_meta([{"seconds": 5.0}], [])
    assert meta[0]["file_id"] == ""
