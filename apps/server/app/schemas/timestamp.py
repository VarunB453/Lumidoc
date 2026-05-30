"""Timestamp extraction Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.schemas.common import ORMModel

TimestampStatus = Literal["pending", "processing", "ready", "failed"]


class TimestampEntry(ORMModel):
    id: str | None = None
    file_id: str
    user_id: str | None = None
    topic: str = Field(..., min_length=1, max_length=300)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., ge=0)
    summary: str = ""
    created_at: datetime | None = None

    @field_validator("end_time")
    @classmethod
    def _validate_end(cls, v: float, info) -> float:
        start = info.data.get("start_time", 0)
        if v < start:
            raise ValueError("end_time must be >= start_time")
        return v


class TimestampListResponse(ORMModel):
    file_id: str
    status: TimestampStatus
    entries: list[TimestampEntry] = Field(default_factory=list)


class TimestampStatusResponse(ORMModel):
    file_id: str
    status: TimestampStatus
    task_id: str | None = None
    message: str | None = None
