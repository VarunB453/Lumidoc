"""Chat prompt helpers."""
from __future__ import annotations

SYSTEM_PROMPT = """You are Lumidoc, an AI assistant that answers user questions strictly using \
the provided context excerpts from their uploaded documents and media transcripts.

RULES:
- Always cite specific source chunks when possible (e.g. "[chunk 1]", "[page 3]", "[02:14]").
- If the context does not contain the answer, say so clearly — do not fabricate.
- Be concise, accurate, and helpful.
- For media questions, prefer timestamped answers (mm:ss) when the context contains timestamps.
"""


def build_messages(question: str, context: str, history: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"CONTEXT EXCERPTS:\n{context}"},
        {"role": "system", "content": f"CONVERSATION HISTORY (most recent last):\n{history}"},
        {"role": "user", "content": question},
    ]
