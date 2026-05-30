"""Backwards-compatible shim.

The transcription service was split into a `services/transcription/` package
for AI-context efficiency. Existing imports keep working through this
re-export. Prefer importing from `app.services.transcription` in new code.
"""
from app.services.transcription import TranscriptionService, transcription_service

__all__ = ["TranscriptionService", "transcription_service"]
