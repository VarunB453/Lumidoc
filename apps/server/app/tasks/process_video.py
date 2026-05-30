"""Celery task: process video (extract audio → reuse audio pipeline)."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.models.file import FileModel
from app.services.embedding_service import embedding_service
from app.services.storage_service import storage_service
from app.services.transcription_service import transcription_service
from app.services.vector_store import vector_store
from app.tasks._processor import celery_processor

logger = get_logger("task.video")


@celery_processor("app.tasks.process_video.process_video", logger_name="task.video")
async def process_video(file_id: str, user_id: str) -> dict[str, Any]:
    file_doc = await FileModel.find_by_id(file_id, user_id)
    if not file_doc:
        raise RuntimeError(f"File {file_id} not found.")
    await FileModel.update_status(file_id, "processing")

    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / Path(file_doc["s3_key"]).name
        await storage_service.download_to_path(file_doc["s3_key"], video_path)

        # Extract audio track via ffmpeg.
        audio_path = Path(tmp) / "audio.mp3"
        transcription_service.extract_audio_track(video_path, audio_path)

        result = await transcription_service.transcribe_long(audio_path, work_dir=tmp)
        segments = result.get("segments", []) or []
        if not segments:
            await FileModel.update_status(
                file_id, "failed", error_message="No transcript produced."
            )
            return {"file_id": file_id, "status": "failed", "chunks": 0}

        chunks = transcription_service.chunk_segments(segments)
        texts = [c["text"] for c in chunks]
        metadatas = [
            {"start_time": c["start_time"], "end_time": c["end_time"]} for c in chunks
        ]
        vectors = await embedding_service.embed_texts(texts)
        await vector_store.upsert(user_id, file_id, vectors, texts, metadatas)

        await FileModel.update_status(
            file_id,
            "ready",
            extra={
                "duration_seconds": float(result.get("duration") or 0.0),
                "transcript_text": result.get("text", "")[:2_000_000],
                "transcript_segments": segments[:10_000],
                "language": result.get("language"),
            },
        )
        logger.info("video_processed", file_id=file_id, chunks=len(chunks))
        return {"file_id": file_id, "status": "ready", "chunks": len(chunks)}
