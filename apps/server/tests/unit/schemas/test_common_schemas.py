"""Unit tests for shared/common Pydantic schemas."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.common import (
    ErrorBody,
    ErrorResponse,
    HealthResponse,
    MessageResponse,
    PaginationMeta,
)


def test_message_response():
    assert MessageResponse(message="ok").message == "ok"


def test_health_response_defaults():
    h = HealthResponse(version="1.0.0")
    assert h.status == "ok"
    assert h.timestamp is not None


def test_pagination_meta_bounds():
    meta = PaginationMeta(page=2, page_size=50, total=120, total_pages=3)
    assert meta.page == 2
    assert meta.page_size == 50

    with pytest.raises(ValidationError):
        PaginationMeta(page=0)
    with pytest.raises(ValidationError):
        PaginationMeta(page_size=101)


def test_error_response_nesting():
    err = ErrorResponse(error=ErrorBody(code="E1", message="boom"))
    assert err.error.code == "E1"
    assert err.error.details is None
