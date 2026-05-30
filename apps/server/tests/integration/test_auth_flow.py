"""Integration tests: full auth flow via HTTP."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_register_login_refresh_logout(client):
    # Register
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "u1@b.com", "password": "Password1", "name": "U1"},
    )
    assert r.status_code == 201
    tokens = r.json()["tokens"]
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    # Protected route
    r = await client.get("/api/v1/files", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200

    # Refresh
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    new_refresh = r.json()["refresh_token"]
    assert new_refresh != refresh

    # Old refresh blacklisted
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 401

    # Logout
    r = await client.post("/api/v1/auth/logout", json={"refresh_token": new_refresh})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_register_duplicate(client):
    payload = {"email": "dup@b.com", "password": "Password1", "name": "D"}
    r1 = await client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "w@b.com", "password": "Password1", "name": "W"},
    )
    r = await client.post("/api/v1/auth/login", json={"email": "w@b.com", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    r = await client.post("/api/v1/auth/login", json={"email": "nope@b.com", "password": "x"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_no_token(client):
    r = await client.get("/api/v1/files")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_bad_token(client):
    r = await client.get("/api/v1/files", headers={"Authorization": "Bearer bad.token"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_validation_error_response(client):
    r = await client.post(
        "/api/v1/auth/register", json={"email": "bad", "password": "x", "name": ""}
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


@pytest.mark.asyncio
async def test_health_and_root(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    r = await client.get("/")
    assert r.status_code == 200
