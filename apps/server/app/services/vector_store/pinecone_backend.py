"""Optional Pinecone backend for the vector store.

Selected when `settings.VECTOR_BACKEND == "pinecone"` and `USE_PINECONE` is
true. The Pinecone SDK is imported lazily so dev/test environments don't pay
the import cost.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any

from app.core.config import settings


class PineconeBackend:
    """Lazy Pinecone client + per-namespace upsert/search helpers."""

    def __init__(self) -> None:
        self._pc = None

    def _get(self):
        if self._pc is None:
            from pinecone import Pinecone

            self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        return self._pc

    async def upsert(
        self,
        namespace: str,
        vectors: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, Any]] | None,
    ) -> list[str]:
        def _do() -> list[str]:
            idx = self._get().Index(settings.PINECONE_INDEX_NAME)
            ids = [uuid.uuid4().hex for _ in vectors]
            items = []
            for i, vid in enumerate(ids):
                md = dict(metadatas[i]) if metadatas else {}
                md["text"] = texts[i]
                items.append({"id": vid, "values": vectors[i], "metadata": md})
            idx.upsert(vectors=items, namespace=namespace)
            return ids

        return await asyncio.to_thread(_do)

    async def search(
        self,
        ns_key_fn,
        user_id: str,
        file_ids: list[str],
        query_vector: list[float],
        top_k: int,
    ) -> list[dict[str, Any]]:
        def _do() -> list[dict[str, Any]]:
            idx = self._get().Index(settings.PINECONE_INDEX_NAME)
            out: list[dict[str, Any]] = []
            for file_id in file_ids:
                namespace = ns_key_fn(user_id, file_id)
                resp = idx.query(
                    vector=query_vector,
                    top_k=top_k,
                    namespace=namespace,
                    include_metadata=True,
                )
                for m in resp.get("matches", []):
                    md = dict(m.get("metadata", {}))
                    md["score"] = m.get("score", 0.0)
                    md["chunk_id"] = m.get("id")
                    md["file_id"] = file_id
                    md["user_id"] = user_id
                    out.append(md)
            out.sort(key=lambda x: x.get("score", 0), reverse=True)
            return out[:top_k]

        return await asyncio.to_thread(_do)
