"""OpenAI Whisper transport: lazy AsyncOpenAI client + a single transcribe call."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger("whisper")


class WhisperClient:
    """Wraps the OpenAI Whisper transcription endpoint."""

    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client
        self.model = settings.OPENAI_WHISPER_MODEL

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=settings.WHISPER_TIMEOUT_SECONDS,
                http_client=httpx.AsyncClient(
                    timeout=settings.WHISPER_TIMEOUT_SECONDS,
                    follow_redirects=True,
                ),
            )
        return self._client

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def transcribe(self, path: str | Path, time_offset: float = 0.0) -> dict[str, Any]:
        """Transcribe one file → {text, segments:[{start,end,text}], language, duration}."""
        path = Path(path)
        try:
            with open(path, "rb") as fh:
                resp = await self.client.audio.transcriptions.create(
                    model=self.model,
                    file=(path.name, fh),
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    timeout=settings.WHISPER_TIMEOUT_SECONDS,
                )
        except Exception as e:
            logger.error("whisper_failed", error=str(e), file=str(path))
            raise ExternalServiceError(f"Whisper transcription failed: {e}") from e

        data = resp.model_dump() if hasattr(resp, "model_dump") else dict(resp)
        segments = [
            {
                "start": float(seg.get("start", 0.0)) + time_offset,
                "end": float(seg.get("end", 0.0)) + time_offset,
                "text": (seg.get("text") or "").strip(),
            }
            for seg in (data.get("segments") or [])
        ]
        return {
            "text": data.get("text", "") or "",
            "segments": segments,
            "language": data.get("language"),
            "duration": float(data.get("duration", 0.0) or 0.0),
        }
