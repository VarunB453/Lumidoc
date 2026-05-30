"""Backwards-compatible shim.

The chat service was split into a `services/chat/` package for AI-context
efficiency and clearer separation of concerns. Existing imports
(`from app.services.chat_service import ChatService, chat_service`) keep
working through this re-export.

Prefer importing from `app.services.chat` in new code.
"""
from app.services.chat import ChatService, chat_service

__all__ = ["ChatService", "chat_service"]
