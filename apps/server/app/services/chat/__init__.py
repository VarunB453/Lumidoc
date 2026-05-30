"""Chat service package — RAG retrieval + Gemini generation, split by concern.

Public exports:
    ChatService      — orchestrator class
    chat_service     — module-level singleton

Sub-modules (private):
    prompts.py       — system prompt + ChatPromptTemplate
    llm.py           — lazy Gemini client factories (sync + streaming)
    retrieval.py     — vector retrieval, dedupe, context/history formatting,
                       timestamp regex extraction
    conversation.py  — conversation CRUD + ownership checks
    service.py       — composition: answer() + stream_answer()
"""
from app.services.chat.service import ChatService, chat_service

__all__ = ["ChatService", "chat_service"]
