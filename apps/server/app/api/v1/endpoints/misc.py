"""Miscellaneous AI utility endpoints: translate, voice → text."""
from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

import google.generativeai as genai
import httpx
from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, ValidationError
from app.integrations.gemini_client import configure_once, get_model
from app.middleware.auth import get_current_user_id

router = APIRouter(tags=["misc"])


def _ensure_gemini() -> None:
    """Backwards-compatible alias kept for any external callers."""
    configure_once()


# ---------- Translate ----------
class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)
    target_language: str = Field(..., min_length=2, max_length=40)
    source_language: str | None = None


class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str


@router.post("/translate", response_model=TranslateResponse)
async def translate(
    payload: TranslateRequest,
    _user_id: str = Depends(get_current_user_id),
) -> TranslateResponse:
    if not settings.GOOGLE_API_KEY:
        raise ExternalServiceError("Translation service is not configured.")
    src = f"from {payload.source_language} " if payload.source_language else ""
    try:
        model = get_model(
            system_instruction=(
                f"You are a precise translator. Translate the user's text {src}"
                f"into {payload.target_language}. Preserve formatting and meaning. "
                "Return ONLY the translation, with no commentary or quotation marks."
            ),
        )
        response = model.generate_content(
            payload.text,
            generation_config=genai.GenerationConfig(
                temperature=0.0,
                max_output_tokens=2000,
            ),
        )
        out = (response.text or "").strip()
        return TranslateResponse(translated_text=out, target_language=payload.target_language)
    except Exception as e:
        raise ExternalServiceError(f"Translation failed: {e}") from e


# ---------- Voice transcription ----------
class VoiceTranscribeResponse(BaseModel):
    text: str
    duration_seconds: float | None = None


@router.post("/voice/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_voice(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
    _user_id: str = Depends(get_current_user_id),
) -> VoiceTranscribeResponse:
    """One-shot Whisper transcription for short voice messages (<25 MB)."""
    if not settings.OPENAI_API_KEY:
        raise ExternalServiceError("Transcription service is not configured.")
    data = await file.read()
    if len(data) == 0:
        raise ValidationError("Empty audio.")
    if len(data) > 25 * 1024 * 1024:
        raise ValidationError("Voice messages must be under 25 MB.")

    suffix = Path(file.filename or "audio.webm").suffix.lower() or ".webm"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(data)
        tmp.flush()
        tmp.close()

        def _call() -> dict:
            with open(tmp.name, "rb") as fh:
                # SDK >= 1.x: openai.audio.transcriptions.create
                from openai import OpenAI

                with httpx.Client(
                    timeout=settings.WHISPER_TIMEOUT_SECONDS,
                    follow_redirects=True,
                ) as http_client:
                    sync_client = OpenAI(
                        api_key=settings.OPENAI_API_KEY,
                        timeout=settings.WHISPER_TIMEOUT_SECONDS,
                        http_client=http_client,
                    )
                    kwargs = {
                        "model": settings.OPENAI_WHISPER_MODEL,
                        "file": fh,
                        "response_format": "verbose_json",
                    }
                    if language:
                        kwargs["language"] = language
                    resp = sync_client.audio.transcriptions.create(**kwargs)
                if hasattr(resp, "model_dump"):
                    return resp.model_dump()
                return dict(resp)

        result = await asyncio.to_thread(_call)
        return VoiceTranscribeResponse(
            text=str(result.get("text", "")).strip(),
            duration_seconds=result.get("duration"),
        )
    except Exception as e:
        raise ExternalServiceError(f"Transcription failed: {e}") from e
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
