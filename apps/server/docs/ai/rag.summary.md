# RAG (embedding + vectors + summary + timestamps) — AI Context Card

## Embedding
- `embedding_service.embed_texts(list[str]) -> list[list[float]]` — batches of 100, retried 3× exp-backoff.
- `embedding_service.embed_query(str) -> list[float]` — single query, `task_type="retrieval_query"`.
- Model: `settings.GEMINI_EMBEDDING_MODEL` (default `text-embedding-004`).
- Dim: `settings.EMBEDDING_DIM` (default 768) — must match the FAISS index.

## Vector store
- Namespace key: `f"{user_id}__{file_id}"` — strict per-user, per-file isolation.
- FAISS `IndexFlatIP` on L2-normalized vectors (cosine equivalent). One index per namespace, persisted as `<namespace>.faiss` + `<namespace>.meta.json` under `FAISS_INDEX_DIR`.
- Pinecone fallback when `VECTOR_BACKEND=pinecone` and `USE_PINECONE=true`.
- `vector_store.search(user_id, file_ids, qvec, top_k=8)` searches each file namespace and merges/sorts.

## Summaries
- `summary_service.get_or_generate(file_id, user_id)` — Redis cache (24h) → Mongo `summaries` upsert → LlamaIndex `TreeSummarize` (with Gemini fallback).
- One summary per file (unique index on `summaries.file_id`).

## Timestamps (audio/video only)
- `timestamp_service.get_cached_or_generate` — Redis cache (12h) → Mongo `timestamp_entries` → LLM segmentation over chunked transcript.
- LLM is forced to `response_mime_type="application/json"` returning `{"topics":[{topic,start_time,end_time,summary}, ...]}`.
- `_sanitize` clamps times into the actual transcript range and dedupes.

## Gotchas
- The summarizer reconfigures LlamaIndex `Settings.llm` and `Settings.embed_model` *globally* on each invocation — fine in single-tenant workers, but watch for races if you ever embed both in the same process.
- Gemini configuration should now go through `app.integrations.gemini_client.configure_once()` / `get_model()` to avoid duplicating `genai.configure()`.
