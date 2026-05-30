"""VectorStore composition: FAISS (default) with optional Pinecone fallback.

Public API (preserved 1:1):
    upsert(user_id, file_id, vectors, texts, metadatas) -> list[str]
    search(user_id, file_ids, query_vector, top_k=8)    -> list[dict]
    delete_namespace(user_id, file_id)                  -> None
    get_all_chunks(user_id, file_id)                    -> list[dict]
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.services.vector_store.faiss_backend import FAISSNamespace
from app.services.vector_store.pinecone_backend import PineconeBackend

logger = get_logger("vector_store")


class VectorStore:
    """High-level wrapper around per-namespace FAISS indices (with Pinecone fallback)."""

    def __init__(self) -> None:
        self.dim = settings.EMBEDDING_DIM
        self.backend = settings.VECTOR_BACKEND
        self.index_dir = Path(settings.FAISS_INDEX_DIR)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, FAISSNamespace] = {}
        self._locks_guard = asyncio.Lock()
        self._locks: dict[str, asyncio.Lock] = {}
        self._pinecone = PineconeBackend()

    # ---------- namespace helpers ----------
    @staticmethod
    def _ns_key(user_id: str, file_id: str) -> str:
        return f"{user_id}__{file_id}"

    def _ns_path(self, namespace: str) -> Path:
        return self.index_dir / f"{namespace}.faiss"

    def _ns_meta_path(self, namespace: str) -> Path:
        return self.index_dir / f"{namespace}.meta.json"

    async def _namespace_lock(self, namespace: str) -> asyncio.Lock:
        async with self._locks_guard:
            lock = self._locks.get(namespace)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[namespace] = lock
            return lock

    async def _load_namespace(self, namespace: str) -> FAISSNamespace:
        if namespace in self._cache:
            return self._cache[namespace]
        path = self._ns_path(namespace)
        if path.exists():
            blob = path.read_bytes()
            ns = await asyncio.to_thread(FAISSNamespace.deserialize, blob)
        else:
            ns = FAISSNamespace(dim=self.dim)
        self._cache[namespace] = ns
        return ns

    async def _persist_namespace(self, namespace: str, ns: FAISSNamespace) -> None:
        path = self._ns_path(namespace)
        blob = await asyncio.to_thread(ns.serialize)
        path.write_bytes(blob)
        meta = {"namespace": namespace, "size": len(ns.ids), "dim": ns.dim}
        self._ns_meta_path(namespace).write_text(json.dumps(meta))

    def _use_pinecone(self) -> bool:
        return self.backend == "pinecone" and settings.USE_PINECONE

    # ---------- public API ----------
    async def upsert(
        self,
        user_id: str,
        file_id: str,
        vectors: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        """Upsert vectors into a user/file namespace; returns new chunk ids."""
        namespace = self._ns_key(user_id, file_id)
        if self._use_pinecone():
            return await self._pinecone.upsert(namespace, vectors, texts, metadatas)
        async with await self._namespace_lock(namespace):
            ns = await self._load_namespace(namespace)
            ids = ns.add(vectors, texts, metadatas)
            await self._persist_namespace(namespace, ns)
            logger.info("vector_upsert", namespace=namespace, count=len(ids))
            return ids

    async def search(
        self,
        user_id: str,
        file_ids: list[str] | None,
        query_vector: list[float],
        top_k: int = 8,
    ) -> list[dict[str, Any]]:
        """Search across one or many file namespaces, returning sorted hits with metadata."""
        if not file_ids:
            return []
        if self._use_pinecone():
            return await self._pinecone.search(
                self._ns_key, user_id, file_ids, query_vector, top_k
            )
        results: list[dict[str, Any]] = []
        for file_id in file_ids:
            namespace = self._ns_key(user_id, file_id)
            try:
                ns = await self._load_namespace(namespace)
            except Exception as e:
                logger.warning("vector_load_failed", namespace=namespace, error=str(e))
                continue
            hits = ns.search(query_vector, top_k=top_k)
            for h in hits:
                h["file_id"] = file_id
                h["user_id"] = user_id
            results.extend(hits)
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    async def delete_namespace(self, user_id: str, file_id: str) -> None:
        namespace = self._ns_key(user_id, file_id)
        async with await self._namespace_lock(namespace):
            self._cache.pop(namespace, None)
            for p in (self._ns_path(namespace), self._ns_meta_path(namespace)):
                if p.exists():
                    p.unlink()
        logger.info("namespace_deleted", namespace=namespace)

    async def get_all_chunks(self, user_id: str, file_id: str) -> list[dict[str, Any]]:
        """Return every chunk's metadata + text for a single namespace (used by summarizer)."""
        namespace = self._ns_key(user_id, file_id)
        try:
            ns = await self._load_namespace(namespace)
        except Exception:
            return []
        return [dict(md) for md in ns.metadata.values()]


vector_store = VectorStore()
