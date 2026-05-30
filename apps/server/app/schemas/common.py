"""Shared Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base Pydantic model with strict typing + arbitrary types allowed."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        # Allow fields that begin with `model_` (e.g. `model_used`) without
        # colliding with Pydantic's reserved namespace.
        protected_namespaces=(),
    )


class MessageResponse(ORMModel):
    message: str


class HealthResponse(ORMModel):
    status: str = "ok"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationMeta(ORMModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    total: int = 0
    total_pages: int = 0


class Page(ORMModel, Generic[T]):
    items: list[T] = Field(default_factory=list)
    meta: PaginationMeta


class ErrorBody(ORMModel):
    code: str
    message: str
    details: object | None = None


class ErrorResponse(ORMModel):
    error: ErrorBody
