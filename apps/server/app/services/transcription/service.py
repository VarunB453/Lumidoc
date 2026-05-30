"""TranscriptionService composition: ffmpeg + Whisper + chunker.

Public surface (preserved 1:1 with the previous monolithic module):
    transcribe_file(path, time_offset=0.0) -> dict
    transcribe_long(audio_path, work_dir)  -> dict
    extract_audio_track(video_path, out_path) -> str
    split_audio(audio_path, work_dir, segment_seconds=None) -> list
    chunk_segments(segments, target_chars, overlap_chars) -> list
    constants: MAX_BYTES, SEGMENT_SECONDS
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from app.services.transcription import ffmpeg as ffmpeg_helpers
from app.services.transcription.chunker import chunk_segments as _chunk_segments
from app.services.transcription.whisper import WhisperClient


class TranscriptionService:
    """Orchestrates audio extraction, Whisper transcription, and segment chunking."""

    MAX_BYTES = 24 * 1024 * 1024            # stay below the 25MB Whisper limit
    SEGMENT_SECONDS = ffmpeg_helpers.DEFAULT_SEGMENT_SECONDS

    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._whisper = WhisperClient(client=client)

    # ---- legacy attribute access kept for back-compat ----
    @property
    def client(self) -> AsyncOpenAI:
        return self._whisper.client

    @property
    def model(self) -> str:
        return self._whisper.model

    # ---- ffmpeg helpers (back-compat classmethods/staticmethods) ----
    @classmethod
    def extract_audio_track(cls, video_path: str | Path, out_path: str | Path) -> str:
        return ffmpeg_helpers.extract_audio_track(video_path, out_path)

    @classmethod
    def split_audio(
        cls,
        audio_path: str | Path,
        work_dir: str | Path,
        segment_seconds: int | None = None,
    ) -> list[dict[str, Any]]:
        return ffmpeg_helpers.split_audio(
            audio_path, work_dir, segment_seconds or cls.SEGMENT_SECONDS
        )

    # ---- whisper ----
    async def transcribe_file(
        self, path: str | Path, time_offset: float = 0.0
    ) -> dict[str, Any]:
        return await self._whisper.transcribe(path, time_offset=time_offset)

    async def transcribe_long(
        self, audio_path: str | Path, work_dir: str | Path
    ) -> dict[str, Any]:
        """Transcribe a potentially long audio file (auto-splits + concatenates)."""
        size = Path(audio_path).stat().st_size
        if size <= self.MAX_BYTES:
            return await self.transcribe_file(audio_path, time_offset=0.0)

        segments_paths = self.split_audio(audio_path, work_dir)
        full_text_parts: list[str] = []
        all_segments: list[dict[str, Any]] = []
        total_duration = 0.0
        language: str | None = None

        for seg in segments_paths:
            result = await self.transcribe_file(seg["path"], time_offset=seg["start"])
            full_text_parts.append(result["text"])
            all_segments.extend(result["segments"])
            total_duration = max(total_duration, seg["end"])
            language = language or result.get("language")

        return {
            "text": "\n".join(full_text_parts).strip(),
            "segments": all_segments,
            "language": language,
            "duration": total_duration,
        }

    # ---- chunker ----
    @staticmethod
    def chunk_segments(
        segments: list[dict[str, Any]],
        target_chars: int = 800,
        overlap_chars: int = 100,
    ) -> list[dict[str, Any]]:
        return _chunk_segments(segments, target_chars=target_chars, overlap_chars=overlap_chars)


transcription_service = TranscriptionService()
