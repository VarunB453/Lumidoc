"""Celery task: process an uploaded PDF (extract → chunk → embed → index)."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.models.file import FileModel
from app.services.embedding_service import embedding_service
from app.services.pdf_service import pdf_service
from app.services.storage_service import storage_service
from app.services.vector_store import vector_store
from app.tasks._processor import celery_processor

logger = get_logger("task.pdf")


@celery_processor("app.tasks.process_pdf.process_pdf", logger_name="task.pdf")
async def process_pdf(file_id: str, user_id: str) -> dict[str, Any]:
    file_doc = await FileModel.find_by_id(file_id, user_id)
    if not file_doc:
        raise RuntimeError(f"File {file_id} not found.")
    await FileModel.update_status(file_id, "processing")

    with tempfile.TemporaryDirectory() as tmp:
        local_path = Path(tmp) / Path(file_doc["s3_key"]).name
        await storage_service.download_to_path(file_doc["s3_key"], local_path)

        pages = pdf_service.extract_text(local_path)
        chunks = pdf_service.chunk_pages(pages)
        if not chunks:
            await FileModel.update_status(
                file_id, "failed", error_message="No extractable text."
            )
            return {"file_id": file_id, "status": "failed", "chunks": 0}

        texts = [c["text"] for c in chunks]
        metadatas = [{"page": c["page"]} for c in chunks]
        vectors = await embedding_service.embed_texts(texts)
        await vector_store.upsert(user_id, file_id, vectors, texts, metadatas)

        await FileModel.update_status(
            file_id, "ready", extra={"page_count": len(pages)}
        )
        logger.info("pdf_processed", file_id=file_id, chunks=len(chunks), pages=len(pages))
        return {"file_id": file_id, "status": "ready", "chunks": len(chunks)}
