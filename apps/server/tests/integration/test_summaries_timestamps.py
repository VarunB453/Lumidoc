"""Integration tests: summaries + timestamps endpoints."""
from __future__ import annotations

import io

import pytest


async def _upload_and_index_pdf(client, headers, user_id):
    files = {"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4 hello"), "application/pdf")}
    r = await client.post("/api/v1/files/upload", headers=headers, files=files)
    fid = r.json()["file_id"]
    from app.services.vector_store import vector_store

    await vector_store.upsert(
        user_id, fid, [[0.1] * 768, [0.2] * 768], ["t1", "t2"], [{"page": 1}, {"page": 2}]
    )
    return fid


async def _upload_and_index_audio(client, headers, user_id):
    files = {"file": ("a.mp3", io.BytesIO(b"\xff\xfbtest"), "audio/mpeg")}
    r = await client.post("/api/v1/files/upload", headers=headers, files=files)
    fid = r.json()["file_id"]
    from app.services.vector_store import vector_store

    await vector_store.upsert(
        user_id,
        fid,
        [[0.1] * 768, [0.2] * 768],
        ["intro text", "more text"],
        [
            {"start_time": 0.0, "end_time": 30.0},
            {"start_time": 30.0, "end_time": 60.0},
        ],
    )
    return fid


@pytest.mark.asyncio
async def test_summary_trigger_and_get(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    fid = await _upload_and_index_pdf(client, headers, auth_headers["user"]["id"])

    r = await client.post(f"/api/v1/summaries/{fid}", headers=headers)
    assert r.status_code == 202

    r = await client.get(f"/api/v1/summaries/{fid}", headers=headers)
    assert r.status_code == 200
    assert "FAKE SUMMARY" in r.json()["content"]


@pytest.mark.asyncio
async def test_summary_missing_file(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    r = await client.post(
        "/api/v1/summaries/507f1f77bcf86cd799439011", headers=headers
    )
    assert r.status_code == 404
    r = await client.get("/api/v1/summaries/507f1f77bcf86cd799439011", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_timestamps_trigger_get_search(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    fid = await _upload_and_index_audio(client, headers, auth_headers["user"]["id"])

    r = await client.post(f"/api/v1/timestamps/{fid}", headers=headers)
    assert r.status_code == 202

    r = await client.get(f"/api/v1/timestamps/{fid}", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "ready"
    assert len(r.json()["entries"]) >= 1

    r = await client.get(f"/api/v1/timestamps/{fid}/Intro", headers=headers)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_timestamps_missing_file(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    r = await client.get(
        "/api/v1/timestamps/507f1f77bcf86cd799439011", headers=headers
    )
    assert r.status_code == 404
