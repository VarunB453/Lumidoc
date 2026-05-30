"""Transcription package — Whisper + ffmpeg + chunker, split by concern.

Public exports:
    TranscriptionService       — orchestrator class (preserved API)
    transcription_service      — module-level singleton

Sub-modules (private):
    ffmpeg.py     — pure ffmpeg/ffprobe helpers (extract, split, probe)
    whisper.py    — OpenAI Whisper API call with retry
    chunker.py    — group Whisper segments into RAG-ready chunks
    service.py    — composition: transcribe_file / transcribe_long
"""
from app.services.transcription.service import (
    TranscriptionService,
    transcription_service,
)

__all__ = ["TranscriptionService", "transcription_service"]
