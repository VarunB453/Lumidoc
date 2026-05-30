"""Unit tests for chat / conversation Pydantic schemas."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.chat import (
    ConversationCreate,
    MessageCreate,
    SourceChunk,
    TimestampRef,
)


def test_conversation_create_defaults():
    c = ConversationCreate()
    assert c.title is None
    assert c.file_ids == []


def test_conversation_create_with_files():
    c = ConversationCreate(title="Notes", file_ids=["a", "b"])
    assert c.title == "Notes"
    assert c.file_ids == ["a", "b"]


def test_message_create_requires_content():
    with pytest.raises(ValidationError):
        MessageCreate(content="")


def test_message_create_rejects_overlong_content():
    with pytest.raises(ValidationError):
        MessageCreate(content="x" * 8001)


def test_message_create_stream_default_false():
    assert MessageCreate(content="hi").stream is False


def test_source_chunk_optional_media_fields():
    chunk = SourceChunk(file_id="f", chunk_id="c", text="t", score=0.5)
    assert chunk.start_time is None
    assert chunk.page is None


def test_timestamp_ref_requires_times():
    ref = TimestampRef(file_id="f", start_time=1.0, end_time=2.0, topic="Intro")
    assert ref.topic == "Intro"
    with pytest.raises(ValidationError):
        TimestampRef(file_id="f", start_time=1.0)  # type: ignore[call-arg]
