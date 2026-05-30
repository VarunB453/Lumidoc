"""End-to-end tests: upload → process → query → verify."""
from __future__ import annotations

import io

import pytest


@pytest.mark.asyncio
async def test_e2e_pdf_upload_chat_cites(client, auth_headers):
    """Upload PDF → seed embeddings → ask question → verify response includes content."""
    headers = {"Authorization": auth_headers["Authorization"]}
    user_id = auth_headers["user"]["id"]

    # 1. Upload
    files = {"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4 ..."), "application/pdf")}
    r = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert r.status_code == 201
    file_id = r.json()["file_id"]

    # 2. Simulate processed (PDF pipeline already tested in unit tests).
    from app.models.file import FileModel
    from app.services.vector_store import vector_store

    await FileModel.update_status(file_id, "ready")
    await vector_store.upsert(
        user_id,
        file_id,
        [[0.1] * 768],
        ["The capital of France is Paris."],
        [{"page": 1}],
    )

    # 3. Conversation + ask
    r = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"title": "Q", "file_ids": [file_id]},
    )
    conv_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/chat/conversations/{conv_id}/messages",
        headers=headers,
        json={"content": "What is the capital of France?"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["role"] == "assistant"
    # In the fake LLM, response contains a timestamp 01:23 → should produce ts_refs
    assert len(body["timestamp_refs"]) >= 1


@pytest.mark.asyncio
async def test_e2e_audio_timestamps(client, auth_headers):
    """Upload audio → simulate processed → get timestamps → verify time format."""
    headers = {"Authorization": auth_headers["Authorization"]}
    user_id = auth_headers["user"]["id"]

    files = {"file": ("clip.mp3", io.BytesIO(b"\xff\xfbtest"), "audio/mpeg")}
    r = await client.post("/api/v1/files/upload", headers=headers, files=files)
    file_id = r.json()["file_id"]

    from app.models.file import FileModel
    from app.services.vector_store import vector_store

    await FileModel.update_status(file_id, "ready")
    await vector_store.upsert(
        user_id,
        file_id,
        [[0.1] * 768, [0.2] * 768],
        ["intro segment", "main topic"],
        [{"start_time": 0.0, "end_time": 30.0}, {"start_time": 30.0, "end_time": 60.0}],
    )

    r = await client.get(f"/api/v1/timestamps/{file_id}", headers=headers)
    assert r.status_code == 200
    entries = r.json()["entries"]
    assert len(entries) >= 1
    for e in entries:
        assert e["start_time"] >= 0.0
        assert e["end_time"] >= e["start_time"]
        assert e["topic"]
