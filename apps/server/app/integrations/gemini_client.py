"""Shared Google Generative AI configuration helper.

`google.generativeai.configure(...)` is process-global, so calling it once is
sufficient. This helper makes that idempotent and removes the
`_configured = False` flag that was duplicated across services.
"""
from __future__ import annotations

import google.generativeai as genai

from app.core.config import settings

_configured = False


def configure_once() -> None:
    """Configure the genai SDK exactly once per process."""
    global _configured
    if not _configured:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        _configured = True


def get_model(
    model_name: str | None = None,
    *,
    system_instruction: str | None = None,
) -> genai.GenerativeModel:
    """Return a configured GenerativeModel. Caller chooses the model name."""
    configure_once()
    return genai.GenerativeModel(
        model_name or settings.GEMINI_MODEL,
        system_instruction=system_instruction,
    )


__all__ = ["configure_once", "get_model"]
