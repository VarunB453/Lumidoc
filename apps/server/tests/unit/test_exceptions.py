"""Unit tests for custom exceptions + global handlers."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import (
    AppException,
    ConflictError,
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnauthorizedError,
    ValidationError,
    register_exception_handlers,
)


def test_app_exception_to_dict():
    err = AppException(message="boom", details={"k": 1})
    d = err.to_dict()
    assert d["error"]["code"] == "internal_error"
    assert d["error"]["message"] == "boom"
    assert d["error"]["details"] == {"k": 1}


@pytest.mark.parametrize(
    "exc_cls,status_code,code",
    [
        (NotFoundError, 404, "not_found"),
        (UnauthorizedError, 401, "unauthorized"),
        (ForbiddenError, 403, "forbidden"),
        (ValidationError, 422, "validation_error"),
        (ConflictError, 409, "conflict"),
        (RateLimitError, 429, "rate_limited"),
        (ServiceUnavailableError, 503, "service_unavailable"),
        (ExternalServiceError, 502, "external_service_error"),
    ],
)
def test_exception_status_codes(exc_cls, status_code, code):
    err = exc_cls()
    assert err.status_code == status_code
    assert err.error_code == code


def test_global_handlers_registered():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/notfound")
    async def _nf():
        raise NotFoundError("missing")

    @app.get("/bad")
    async def _bad():
        raise RuntimeError("explode")

    @app.get("/http")
    async def _http():
        from fastapi import HTTPException

        raise HTTPException(status_code=418, detail="teapot")

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/notfound")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"

    r = client.get("/bad")
    assert r.status_code == 500
    assert r.json()["error"]["code"] == "internal_error"

    r = client.get("/http")
    assert r.status_code == 418
    assert r.json()["error"]["code"] == "http_error"
