"""Vector store package — FAISS namespaces + optional Pinecone backend, split.

Public exports (preserved API):
    VectorStore        — high-level orchestrator class
    FAISSNamespace     — single-namespace FAISS index + metadata
    vector_store       — module-level singleton

Sub-modules (private):
    faiss_backend.py   — FAISSNamespace (one index per user/file)
    pinecone_backend.py — Pinecone upsert/search helpers (lazy import)
    store.py           — VectorStore composition + caching + dispatch
"""
from app.services.vector_store.faiss_backend import FAISSNamespace
from app.services.vector_store.store import VectorStore, vector_store

__all__ = ["FAISSNamespace", "VectorStore", "vector_store"]
