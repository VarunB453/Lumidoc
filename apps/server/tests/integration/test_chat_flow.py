"""Integration tests: chat conversations + messages + streaming."""
from __future__ import annotations

import io

import pytest


async def _upload_pdf(client, headers) -> str:
    files = {"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4 hello"), "application/pdf")}
    r = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert r.status_code == 201
    return r.json()["file_id"]


@pytest.mark.asyncio
async def test_create_list_get_conversation(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    fid = await _upload_pdf(client, headers)

    r = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"title": "Hi", "file_ids": [fid]},
    )
    assert r.status_code == 201
    conv_id = r.json()["id"]

    r = await client.get("/api/v1/chat/conversations", headers=headers)
    assert r.status_code == 200
    assert any(c["id"] == conv_id for c in r.json())

    r = await client.get(f"/api/v1/chat/conversations/{conv_id}", headers=headers)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_send_message_and_history(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    fid = await _upload_pdf(client, headers)
    # Seed vector store so retrieval returns chunks.
    from app.services.vector_store import vector_store

    await vector_store.upsert(
        auth_headers["user"]["id"], fid, [[0.1] * 768], ["ctx text"], [{"page": 1}]
    )

    r = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"title": "Q", "file_ids": [fid]},
    )
    conv_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/chat/conversations/{conv_id}/messages",
        headers=headers,
        json={"content": "What is this?"},
    )
    assert r.status_code == 201
    assert r.json()["role"] == "assistant"

    r = await client.get(
        f"/api/v1/chat/conversations/{conv_id}/messages", headers=headers
    )
    assert r.status_code == 200
    assert len(r.json()) == 2


@pytest.mark.asyncio
async def test_create_conversation_with_invalid_file(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    r = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"title": "X", "file_ids": ["507f1f77bcf86cd799439011"]},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_chat_stream_endpoint(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    fid = await _upload_pdf(client, headers)
    r = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"title": "S", "file_ids": [fid]},
    )
    conv_id = r.json()["id"]

    r = await client.get(
        f"/api/v1/chat/conversations/{conv_id}/messages/stream",
        headers=headers,
        params={"q": "Hello?"},
    )
    assert r.status_code == 200
    body = r.text
    assert "event:" in body or "data:" in body
