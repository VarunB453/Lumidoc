"""Unit tests for TranscriptionService (chunking + fake transcribe)."""
from __future__ import annotations

import pytest

from app.services.transcription_service import TranscriptionService, transcription_service


def test_chunk_segments_basic():
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Hello world. " * 20},
        {"start": 2.0, "end": 4.0, "text": "Second segment text. " * 20},
        {"start": 4.0, "end": 6.0, "text": "Third one."},
    ]
    chunks = transcription_service.chunk_segments(segments, target_chars=200, overlap_chars=50)
    assert len(chunks) >= 1
    for c in chunks:
        assert "text" in c
        assert "start_time" in c
        assert "end_time" in c
        assert c["end_time"] >= c["start_time"]


def test_chunk_segments_empty():
    assert transcription_service.chunk_segments([]) == []


def test_chunk_segments_skips_empty_text():
    segments = [
        {"start": 0.0, "end": 1.0, "text": ""},
        {"start": 1.0, "end": 2.0, "text": "Real text. " * 50},
    ]
    chunks = transcription_service.chunk_segments(segments, target_chars=100)
    assert all(c["text"] for c in chunks)


@pytest.mark.asyncio
async def test_transcribe_file_via_fake(tmp_path):
    f = tmp_path / "fake.mp3"
    f.write_bytes(b"FAKE")
    result = await transcription_service.transcribe_file(f)
    assert "text" in result
    assert result["segments"][0]["start"] == 0.0


@pytest.mark.asyncio
async def test_transcribe_long_via_fake(tmp_path):
    f = tmp_path / "fake.mp3"
    f.write_bytes(b"FAKE")
    result = await transcription_service.transcribe_long(f, work_dir=tmp_path)
    assert result["segments"]


def test_constants():
    assert TranscriptionService.MAX_BYTES > 0
    assert TranscriptionService.SEGMENT_SECONDS == 600
