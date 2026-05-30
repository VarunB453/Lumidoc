"""Retrieval helpers: vector search, dedupe, context/history formatting,
and inline-timestamp regex extraction.

Pure functions / small helpers — keep this module side-effect free so
unit tests can import without spinning up the LLM.
"""
from __future__ import annotations

import re
from typing import Any

from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store

TOP_K_DEFAULT = 8
HISTORY_TURNS_DEFAULT = 10

_TIMESTAMP_RE = re.compile(r"\b(\d{1,2}):([0-5]\d)(?::([0-5]\d))?\b")


async def retrieve(
    user_id: str,
    file_ids: list[str],
    question: str,
    *,
    top_k: int = TOP_K_DEFAULT,
) -> list[dict[str, Any]]:
    """Embed the question and search across user's file namespaces.

    Performs a simple text-prefix dedupe (poor-man's MMR) so near-identical
    chunks don't drown out diverse context.
    """
    if not file_ids:
        return []
    qvec = await embedding_service.embed_query(question)
    hits = await vector_store.search(user_id, file_ids, qvec, top_k=top_k)
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for h in hits:
        sig = (h.get("text", "")[:120]).strip()
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(h)
    return unique[:top_k]


def format_context(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "(no relevant context found in user's documents)"
    parts: list[str] = []
    for i, c in enumerate(chunks, 1):
        loc_bits: list[str] = []
        if c.get("page") is not None:
            loc_bits.append(f"page {c['page']}")
        if c.get("start_time") is not None and c.get("end_time") is not None:
            loc_bits.append(f"{c['start_time']:.1f}s–{c['end_time']:.1f}s")
        loc = f" ({', '.join(loc_bits)})" if loc_bits else ""
        parts.append(f"[chunk {i}{loc}]\n{c.get('text','').strip()}")
    return "\n\n".join(parts)


def format_history(history: list[dict[str, Any]]) -> str:
    if not history:
        return "(no prior messages)"
    return "\n".join(
        f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in history
    )


def extract_timestamp_refs(text: str) -> list[dict[str, Any]]:
    """Find inline mm:ss or hh:mm:ss references in the AI's response."""
    refs: list[dict[str, Any]] = []
    for match in _TIMESTAMP_RE.finditer(text):
        h, m, s = match.groups()
        seconds = int(h) * 3600 + int(m) * 60 + int(s) if s is not None else int(h) * 60 + int(m)
        refs.append({"raw": match.group(0), "seconds": float(seconds)})
    return refs


def chunks_to_meta(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compact per-chunk metadata for client/citation rendering."""
    return [
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
    ]


def refs_to_meta(
    timestamp_refs: list[dict[str, Any]], file_ids: list[str]
) -> list[dict[str, Any]]:
    fid = file_ids[0] if file_ids else ""
    return [
        {
            "file_id": fid,
            "start_time": r["seconds"],
            "end_time": r["seconds"],
            "topic": None,
        }
        for r in timestamp_refs
    ]
