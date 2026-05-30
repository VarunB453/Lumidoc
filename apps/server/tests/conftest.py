"""Pytest fixtures: in-memory Mongo + fake Redis + ephemeral JWT keys + AsyncClient."""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

# Force test environment BEFORE importing app modules.
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("USE_LOCAL_STORAGE", "true")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB_NAME", "lumidoc_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("RATE_LIMIT_PER_IP", "10000")
os.environ.setdefault("RATE_LIMIT_PER_USER", "10000")
os.environ.setdefault("EMBEDDING_DIM", "768")

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Make ephemeral key paths inside a tmp dir created per-session.
_TMP = tempfile.mkdtemp(prefix="lumidoc-test-")
os.environ["JWT_PRIVATE_KEY_PATH"] = str(Path(_TMP) / "private.pem")
os.environ["JWT_PUBLIC_KEY_PATH"] = str(Path(_TMP) / "public.pem")
os.environ["LOCAL_STORAGE_PATH"] = str(Path(_TMP) / "storage")
os.environ["FAISS_INDEX_DIR"] = str(Path(_TMP) / "faiss")


# ----------------------- Event loop -----------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ----------------------- Patch external services BEFORE imports propagate -----------------------
@pytest.fixture(autouse=True)
def patch_redis(monkeypatch):
    """Replace the global Redis clients with fakeredis async."""
    import fakeredis.aioredis as fakeredis_aio

    from app.db import redis_client

    fake_cache = fakeredis_aio.FakeRedis(decode_responses=True)
    fake_rl = fakeredis_aio.FakeRedis(decode_responses=True)
    redis_client.RedisClient.cache = fake_cache
    redis_client.RedisClient.ratelimit = fake_rl
    redis_client.RedisClient.available = True
    yield
    # Flush between tests.
    try:
        asyncio.get_event_loop().run_until_complete(fake_cache.flushall())
        asyncio.get_event_loop().run_until_complete(fake_rl.flushall())
    except Exception:
        pass
    redis_client.RedisClient.available = False


@pytest.fixture(autouse=True)
def patch_mongo(monkeypatch):
    """Replace Motor client with mongomock-motor in-memory client."""
    from mongomock_motor import AsyncMongoMockClient

    from app.db import mongodb

    client = AsyncMongoMockClient()
    db = client["lumidoc_test"]
    monkeypatch.setattr(mongodb.MongoDB, "client", client)
    monkeypatch.setattr(mongodb.MongoDB, "db", db)

    async def _noop_connect(*a, **k):
        return None

    async def _noop_disconnect():
        return None

    monkeypatch.setattr(mongodb.MongoDB, "connect", classmethod(lambda cls, *a, **k: _noop_connect()))
    monkeypatch.setattr(mongodb.MongoDB, "disconnect", classmethod(lambda cls: _noop_disconnect()))
    yield


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    """Mock all OpenAI SDK calls so tests never hit the network."""
    import numpy as np

    # ---- embeddings ----
    async def fake_embed_texts(self, texts):
        # Mirror the real implementation: strip whitespace and filter blanks.
        cleaned = [t.strip() for t in texts if t and t.strip()]
        if not cleaned:
            return []
        out = []
        for t in cleaned:
            # deterministic Gemini-sized vector
            seed = abs(hash(t)) % (2**31)
            rng = np.random.RandomState(seed)
            out.append(rng.rand(768).astype(float).tolist())
        return out

    async def fake_embed_query(self, text):
        vecs = await fake_embed_texts(self, [text])
        return vecs[0]

    from app.services import embedding_service as es_mod

    monkeypatch.setattr(es_mod.EmbeddingService, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(es_mod.EmbeddingService, "embed_query", fake_embed_query)

    # ---- transcription ----
    from app.services import transcription_service as ts_mod

    async def fake_transcribe(self, path, time_offset=0.0):
        return {
            "text": "Hello world. This is a fake transcript.",
            "segments": [
                {"start": time_offset + 0.0, "end": time_offset + 2.0, "text": "Hello world."},
                {"start": time_offset + 2.0, "end": time_offset + 4.0, "text": "This is a fake transcript."},
            ],
            "language": "en",
            "duration": 4.0,
        }

    monkeypatch.setattr(ts_mod.TranscriptionService, "transcribe_file", fake_transcribe)
    monkeypatch.setattr(
        ts_mod.TranscriptionService,
        "transcribe_long",
        lambda self, audio_path, work_dir: fake_transcribe(self, audio_path, 0.0),
    )

    # ---- chat service streaming + non-streaming ----
    from app.services import chat_service as cs_mod

    class _FakeChain:
        async def ainvoke(self, _):
            return "Fake assistant answer at 01:23."

        async def astream(self, _):
            for token in ["Fake ", "assistant ", "answer ", "at ", "01:23."]:
                yield token

    def _build_chain(self_):
        return _FakeChain()

    # Patch property access by replacing llm/llm_streaming attrs after instance creation.
    cs_mod.chat_service._llm = MagicMock()
    cs_mod.chat_service._llm_stream = MagicMock()

    # Monkeypatch the LCEL pipeline to use FakeChain directly via .answer/.stream paths.
    original_answer = cs_mod.ChatService.answer
    original_stream = cs_mod.ChatService.stream_answer

    async def fake_answer(self, conv_id, user_id, question):
        from app.core.exceptions import NotFoundError
        from app.models.conversation import ConversationModel
        from app.models.message import MessageModel

        conv = await ConversationModel.find_by_id(conv_id, user_id)
        if not conv:
            raise NotFoundError("Conversation not found.")
        chunks = await self._retrieve(user_id, conv.get("file_ids", []), question)
        user_msg = MessageModel.doc(conv_id, user_id, "user", question)
        user_msg_id = await MessageModel.insert(user_msg)
        text = "Fake assistant answer at 01:23."
        ts_refs = self._extract_timestamp_refs(text)
        ts_refs_meta = [
            {
                "file_id": (conv.get("file_ids") or [""])[0],
                "start_time": r["seconds"],
                "end_time": r["seconds"],
                "topic": None,
            }
            for r in ts_refs
        ]
        ai_msg = MessageModel.doc(
            conv_id,
            user_id,
            "assistant",
            text,
            source_chunks=[
                {
                    "file_id": c.get("file_id", ""),
                    "chunk_id": c.get("chunk_id", ""),
                    "text": c.get("text", "")[:600],
                    "score": c.get("score", 0.0),
                    "start_time": c.get("start_time"),
                    "end_time": c.get("end_time"),
                    "page": c.get("page"),
                }
                for c in chunks
            ],
            timestamp_refs=ts_refs_meta,
        )
        ai_msg_id = await MessageModel.insert(ai_msg)
        await ConversationModel.bump(conv_id, increment_messages=2)
        ai_msg["_id"] = ai_msg_id
        return MessageModel.to_public(ai_msg), {"user_message_id": user_msg_id}

    async def fake_stream(self, conv_id, user_id, question):
        from app.core.exceptions import NotFoundError
        from app.models.conversation import ConversationModel
        from app.models.message import MessageModel

        conv = await ConversationModel.find_by_id(conv_id, user_id)
        if not conv:
            raise NotFoundError("Conversation not found.")
        chunks = await self._retrieve(user_id, conv.get("file_ids", []), question)
        user_msg = MessageModel.doc(conv_id, user_id, "user", question)
        user_msg_id = await MessageModel.insert(user_msg)
        yield {"event": "user_message", "data": {"user_message_id": user_msg_id}}
        yield {"event": "sources", "data": {"chunks": []}}
        full = ""
        for token in ["Fake ", "answer ", "at ", "01:23."]:
            full += token
            yield {"event": "token", "data": {"text": token}}
        ai_msg = MessageModel.doc(conv_id, user_id, "assistant", full)
        ai_msg_id = await MessageModel.insert(ai_msg)
        await ConversationModel.bump(conv_id, increment_messages=2)
        yield {
            "event": "done",
            "data": {"message_id": ai_msg_id, "content": full, "timestamp_refs": []},
        }

    monkeypatch.setattr(cs_mod.ChatService, "answer", fake_answer)
    monkeypatch.setattr(cs_mod.ChatService, "stream_answer", fake_stream)

    # ---- summary service ----
    from app.services import summary_service as ss_mod

    async def fake_summarize(self, chunks):
        return "FAKE SUMMARY: overview + bullets + takeaway."

    monkeypatch.setattr(ss_mod.SummaryService, "_summarize", fake_summarize)

    # ---- timestamp service ----
    from app.services import timestamp_service as tss_mod

    async def fake_call_llm(self, chunks):
        if not chunks:
            return []
        return [
            {
                "topic": "Introduction",
                "start_time": float(chunks[0]["start_time"]),
                "end_time": float(chunks[0]["end_time"]),
                "summary": "Intro segment.",
            }
        ]

    monkeypatch.setattr(tss_mod.TimestampService, "_call_llm", fake_call_llm)
    yield


@pytest.fixture(autouse=True)
def reset_vector_store(monkeypatch):
    """Reset the module-level VectorStore singleton so tests don't leak state.

    Persistence is skipped on the singleton because faiss.serialize_index has a
    known SWIG/Windows bug where it fails with
    `assert classname.endswith('Vector')` after certain import orderings in the
    full test suite. The vector_store unit tests use their own fixture.
    """
    from app.services.vector_store import vector_store

    vector_store._cache.clear()
    import tempfile
    tmp = tempfile.mkdtemp(prefix="faiss-test-")
    monkeypatch.setattr(vector_store, "index_dir", Path(tmp))

    # No-op persistence on the singleton instance only.
    async def _noop_persist(namespace, ns):
        pass

    monkeypatch.setattr(vector_store, "_persist_namespace", _noop_persist)
    yield


@pytest.fixture(autouse=True)
def patch_celery(monkeypatch):
    """Make all .delay() calls inline no-ops (return a mock AsyncResult)."""
    class _R:
        def __init__(self) -> None:
            self.id = "test-task-id"

    def _make_delay(*a, **k):
        return _R()

    import app.tasks.generate_summary as s
    import app.tasks.generate_timestamps as t
    import app.tasks.process_audio as a
    import app.tasks.process_pdf as p
    import app.tasks.process_video as v

    for mod, fname in (
        (p, "process_pdf"),
        (a, "process_audio"),
        (v, "process_video"),
        (s, "generate_summary"),
        (t, "generate_timestamps"),
    ):
        try:
            getattr(mod, fname).delay = _make_delay  # type: ignore[attr-defined]
        except Exception:
            pass
    yield


# ----------------------- Core fixtures -----------------------
@pytest_asyncio.fixture
async def app_instance():
    from app.main import create_app

    app = create_app()
    yield app


@pytest_asyncio.fixture
async def client(app_instance) -> AsyncIterator:
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register a user + return Authorization headers."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "Password123", "name": "Alice"},
    )
    assert resp.status_code == 201, resp.text
    tokens = resp.json()["tokens"]
    return {
        "Authorization": f"Bearer {tokens['access_token']}",
        "refresh_token": tokens["refresh_token"],
        "user": resp.json()["user"],
    }
