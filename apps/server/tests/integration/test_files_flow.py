"""Integration tests: file upload, list, get, delete, download."""
from __future__ import annotations

import io

import pytest


@pytest.mark.asyncio
async def test_full_file_lifecycle(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}

    # Upload
    files = {"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4 hello"), "application/pdf")}
    r = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert r.status_code == 201, r.text
    file_id = r.json()["file_id"]
    assert r.json()["file_type"] == "pdf"

    # List
    r = await client.get("/api/v1/files", headers=headers)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1

    # Get
    r = await client.get(f"/api/v1/files/{file_id}", headers=headers)
    assert r.status_code == 200

    # Download URL
    r = await client.get(f"/api/v1/files/{file_id}/download", headers=headers)
    assert r.status_code == 200
    assert "url" in r.json()

    # Delete
    r = await client.delete(f"/api/v1/files/{file_id}", headers=headers)
    assert r.status_code == 200

    # Get after delete
    r = await client.get(f"/api/v1/files/{file_id}", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_upload_unsupported(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    files = {"file": ("doc.xyz", io.BytesIO(b"data"), "application/octet-stream")}
    r = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_files_isolated_by_user(client):
    # User A
    a = await client.post(
        "/api/v1/auth/register",
        json={"email": "a@x.com", "password": "Password1", "name": "A"},
    )
    a_token = a.json()["tokens"]["access_token"]

    # User B
    b = await client.post(
        "/api/v1/auth/register",
        json={"email": "b@x.com", "password": "Password1", "name": "B"},
    )
    b_token = b.json()["tokens"]["access_token"]

    files = {"file": ("a.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")}
    r = await client.post(
        "/api/v1/files/upload",
        headers={"Authorization": f"Bearer {a_token}"},
        files=files,
    )
    fid = r.json()["file_id"]

    # B cannot see A's file
    r = await client.get(
        f"/api/v1/files/{fid}", headers={"Authorization": f"Bearer {b_token}"}
    )
    assert r.status_code == 404
