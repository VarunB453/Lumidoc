"""Single-namespace FAISS index + per-vector metadata.

One `FAISSNamespace` instance is created per `(user_id, file_id)` pair.
The index uses inner product on L2-normalized vectors, which is
mathematically equivalent to cosine similarity.
"""
from __future__ import annotations

import base64
import json
import uuid
from typing import Any

import numpy as np


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
    return vectors / norms


class FAISSNamespace:
    """A single FAISS index + metadata store for one (user_id, file_id) namespace."""

    def __init__(self, dim: int) -> None:
        import faiss  # local import: heavy dep

        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # inner-product on normalized vectors
        self.ids: list[str] = []
        self.metadata: dict[str, dict[str, Any]] = {}

    def add(
        self,
        vectors: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        if not vectors:
            return []
        arr = np.asarray(vectors, dtype="float32")
        if arr.shape[1] != self.dim:
            raise ValueError(f"Vector dim mismatch: got {arr.shape[1]}, expected {self.dim}")
        arr = _normalize(arr)
        new_ids = [uuid.uuid4().hex for _ in vectors]
        self.index.add(arr)
        for i, vid in enumerate(new_ids):
            self.ids.append(vid)
            md = dict(metadatas[i]) if metadatas and i < len(metadatas) else {}
            md["text"] = texts[i]
            md["chunk_id"] = vid
            self.metadata[vid] = md
        return new_ids

    def search(self, query_vector: list[float], top_k: int = 8) -> list[dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
        q = _normalize(np.asarray([query_vector], dtype="float32"))
        scores, idxs = self.index.search(q, min(top_k, self.index.ntotal))
        out: list[dict[str, Any]] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist(), strict=False):
            if idx < 0 or idx >= len(self.ids):
                continue
            vid = self.ids[idx]
            md = dict(self.metadata.get(vid, {}))
            md["score"] = float(score)
            out.append(md)
        return out

    def serialize(self) -> bytes:
        import faiss

        index_bytes = faiss.serialize_index(self.index)
        payload = {
            "version": 1,
            "dim": self.dim,
            "index_b64": base64.b64encode(bytes(index_bytes)).decode("ascii"),
            "ids": self.ids,
            "metadata": self.metadata,
        }
        return json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")

    @classmethod
    def deserialize(cls, blob: bytes) -> FAISSNamespace:
        import faiss

        try:
            payload = json.loads(blob.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "Unsafe legacy FAISS pickle indexes are not supported; rebuild the index."
            ) from exc
        ns = cls(dim=payload["dim"])
        index_bytes = base64.b64decode(payload["index_b64"])
        ns.index = faiss.deserialize_index(np.frombuffer(index_bytes, dtype="uint8"))
        ns.ids = payload["ids"]
        ns.metadata = payload["metadata"]
        return ns
