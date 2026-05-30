"""Unit tests for Pydantic schemas (validators, coercion)."""
from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.chat import (
    ConversationCreate,
    MessageCreate,
    SourceChunk,
    TimestampRef,
)
from app.schemas.common import HealthResponse, MessageResponse, Page, PaginationMeta
from app.schemas.file import FileMetadata
from app.schemas.summary import SummaryResponse
from app.schemas.timestamp import TimestampEntry
from app.schemas.user import (
    LogoutRequest,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserPublic,
    UserRegister,
)


def test_user_register_rejects_weak_password():
    with pytest.raises(ValidationError):
        UserRegister(email="a@b.com", password="onlyletters", name="X")
    with pytest.raises(ValidationError):
        UserRegister(email="a@b.com", password="12345678", name="X")


def test_user_register_accepts_strong():
    u = UserRegister(email="a@b.com", password="Letters1", name="Alice")
    assert u.name == "Alice"


def test_user_register_short_password():
    with pytest.raises(ValidationError):
        UserRegister(email="a@b.com", password="Ab1", name="X")


def test_user_register_invalid_email():
    with pytest.raises(ValidationError):
        UserRegister(email="not-email", password="Password1", name="X")


def test_user_login_basic():
    u = UserLogin(email="a@b.com", password="x")
    assert u.email == "a@b.com"


def test_refresh_request_min_length():
    with pytest.raises(ValidationError):
        RefreshRequest(refresh_token="short")
    r = RefreshRequest(refresh_token="x" * 20)
    assert r.refresh_token


def test_logout_request():
    r = LogoutRequest(refresh_token="x" * 20)
    assert r.refresh_token


def test_token_pair():
    t = TokenPair(access_token="a", refresh_token="b", expires_in=900)
    assert t.token_type == "bearer"


def test_user_public():
    u = UserPublic(
        id="1",
        email="a@b.com",
        name="A",
        created_at=datetime.utcnow(),
    )
    assert u.role == "user"


def test_message_create():
    m = MessageCreate(content="hi")
    assert m.stream is False
    with pytest.raises(ValidationError):
        MessageCreate(content="")


def test_conversation_create_defaults():
    c = ConversationCreate()
    assert c.file_ids == []
    assert c.title is None


def test_source_chunk_schema():
    s = SourceChunk(file_id="f", chunk_id="c", text="t", score=0.9, page=1)
    assert s.start_time is None


def test_timestamp_ref_schema():
    ts = TimestampRef(file_id="f", start_time=0, end_time=10, topic="Hi")
    assert ts.topic == "Hi"


def test_pagination_meta_defaults():
    m = PaginationMeta()
    assert m.page == 1


def test_page_generic():
    p = Page[MessageResponse](items=[MessageResponse(message="ok")], meta=PaginationMeta())
    assert p.items[0].message == "ok"


def test_health_response_default_ok():
    h = HealthResponse(version="1.0.0")
    assert h.status == "ok"


def test_file_metadata():
    f = FileMetadata(
        id="1",
        user_id="u",
        filename="a.pdf",
        original_name="a.pdf",
        file_type="pdf",
        s3_key="k",
        size_bytes=10,
        status="ready",
        created_at=datetime.utcnow(),
    )
    assert f.is_deleted is False


def test_summary_response():
    s = SummaryResponse(
        id="1",
        file_id="f",
        user_id="u",
        content="text",
        model_used="gpt-4o",
        generated_at=datetime.utcnow(),
    )
    assert s.status == "ready"


def test_timestamp_entry_end_before_start():
    with pytest.raises(ValidationError):
        TimestampEntry(file_id="f", topic="T", start_time=10, end_time=5)


def test_timestamp_entry_valid():
    e = TimestampEntry(file_id="f", topic="T", start_time=0, end_time=10)
    assert e.summary == ""
