"""Chat / conversation Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import ORMModel

MessageRole = Literal["user", "assistant", "system"]


class SourceChunk(ORMModel):
    file_id: str
    chunk_id: str
    text: str
    score: float
    start_time: float | None = None
    end_time: float | None = None
    page: int | None = None


class TimestampRef(ORMModel):
    file_id: str
    start_time: float
    end_time: float
    topic: str | None = None


class ConversationCreate(ORMModel):
    title: str | None = Field(None, max_length=200)
    file_ids: list[str] = Field(default_factory=list)


class ConversationPublic(ORMModel):
    id: str
    user_id: str
    title: str
    file_ids: list[str] = Field(default_factory=list)
    message_count: int = 0
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime


class ConversationUpdate(ORMModel):
    title: str | None = Field(None, max_length=200)
    is_favorite: bool | None = None
    file_ids: list[str] | None = None


class MessageCreate(ORMModel):
    content: str = Field(..., min_length=1, max_length=8000)
    stream: bool = False


class MessagePublic(ORMModel):
    id: str
    conversation_id: str
    user_id: str
    role: MessageRole
    content: str
    source_chunks: list[SourceChunk] = Field(default_factory=list)
    timestamp_refs: list[TimestampRef] = Field(default_factory=list)
    created_at: datetime


class ChatAnswer(ORMModel):
    message: MessagePublic
    user_message_id: str
