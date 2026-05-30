# ADR 0002: Use FAISS for Vector Store

## Status
Accepted

## Context
The application requires vector similarity search for AI/ML features (embeddings, semantic search). Options considered:
- FAISS (Facebook AI Similarity Search)
- Pinecone (managed service)
- Weaviate
- ChromaDB
- pgvector (PostgreSQL extension)

## Decision
We chose **FAISS** as the vector store.

## Rationale
- **Performance**: Highly optimized for similarity search, supports GPU acceleration
- **No External Dependency**: Runs in-process, no additional service to manage
- **Cost**: Free and open-source, no per-query pricing
- **Flexibility**: Supports multiple index types (Flat, IVF, HNSW)
- **Proven**: Battle-tested at scale by Meta

## Consequences
- Vector indices are stored on disk (local or shared storage)
- Need to handle index persistence and backup manually
- May need to migrate to a distributed solution (Pinecone, Weaviate) at scale
- No built-in filtering — need to implement metadata filtering separately
