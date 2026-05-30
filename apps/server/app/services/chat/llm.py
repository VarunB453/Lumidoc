"""Lazy Gemini chat-model factory (sync + streaming variants)."""
from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


class GeminiChatFactory:
    """Owns the two Gemini chat clients (streaming + non-streaming)."""

    def __init__(self) -> None:
        self._llm: ChatGoogleGenerativeAI | None = None
        self._llm_stream: ChatGoogleGenerativeAI | None = None

    def _build(self, *, streaming: bool) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
            google_api_key=settings.GOOGLE_API_KEY,
            streaming=streaming,
            request_timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
        )

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        if self._llm is None:
            self._llm = self._build(streaming=False)
        return self._llm

    @property
    def llm_streaming(self) -> ChatGoogleGenerativeAI:
        if self._llm_stream is None:
            self._llm_stream = self._build(streaming=True)
        return self._llm_stream
