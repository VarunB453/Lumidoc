"""ChatService composition layer.

Glues together the small pieces in `chat/` (prompts, retrieval,
conversation) into the public service used by routers + Celery.

Behavior is preserved 1:1 with the previous monolithic chat_service.py:
    * conversation CRUD
    * non-streaming `answer()` returning a saved assistant message
    * SSE-friendly `stream_answer()` async generator
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.integrations.openrouter_client import create_chat_completion, stream_chat_completion
from app.models.conversation import ConversationModel
from app.models.message import MessageModel
from app.services.chat import conversation as conv_ops
from app.services.chat.prompts import build_messages
from app.services.chat.retrieval import (
    HISTORY_TURNS_DEFAULT,
    TOP_K_DEFAULT,
    chunks_to_meta,
    extract_timestamp_refs,
    format_context,
    format_history,
    refs_to_meta,
    retrieve,
)

logger = get_logger("chat")


class ChatService:
    """Orchestrates RAG retrieval + OpenRouter generation."""

    TOP_K = TOP_K_DEFAULT
    HISTORY_TURNS = HISTORY_TURNS_DEFAULT

    # ---- backwards-compat helpers (used by older callers and unit tests) ----
    # Prefer importing the standalone functions from `app.services.chat.retrieval`.
    _extract_timestamp_refs = staticmethod(extract_timestamp_refs)
    _format_context = staticmethod(format_context)
    _format_history = staticmethod(format_history)

    async def _retrieve(
        self, user_id: str, file_ids: list[str], question: str
    ) -> list[dict[str, Any]]:
        return await retrieve(user_id, file_ids, question, top_k=self.TOP_K)

    # ---- conversation crud (delegated) ----
    async def create_conversation(self, user_id, title, file_ids):
        return await conv_ops.create(user_id, title, file_ids)

    async def list_conversations(self, user_id, only_favorites=False):
        return await conv_ops.list_for_user(user_id, only_favorites=only_favorites)

    async def update_conversation(self, conv_id, user_id, **kwargs):
        return await conv_ops.update(conv_id, user_id, **kwargs)

    async def delete_conversation(self, conv_id, user_id):
        return await conv_ops.delete(conv_id, user_id)

    async def get_conversation(self, conv_id, user_id):
        return await conv_ops.get(conv_id, user_id)

    async def list_messages(self, conv_id, user_id):
        return await conv_ops.list_messages(conv_id, user_id)

    async def _gather_inputs(self, conv_id: str, user_id: str, question: str):
        conv = await ConversationModel.find_by_id(conv_id, user_id)
        if not conv:
            raise NotFoundError("Conversation not found.")
        file_ids = conv.get("file_ids", []) or []
        chunks = await retrieve(user_id, file_ids, question, top_k=self.TOP_K)
        history = await MessageModel.recent_history(conv_id, limit=self.HISTORY_TURNS)
        return file_ids, chunks, format_context(chunks), format_history(history)

    # ---- non-streaming answer ----
    async def answer(
        self, conv_id: str, user_id: str, question: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        file_ids, chunks, context_str, history_str = await self._gather_inputs(
            conv_id, user_id, question
        )

        user_msg_id = await MessageModel.insert(
            MessageModel.doc(conv_id, user_id, "user", question)
        )

        messages = build_messages(question, context_str, history_str)
        try:
            answer_text = await asyncio.wait_for(
                create_chat_completion(messages),
                timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
            )
        except TimeoutError:
            logger.exception("llm_timeout")
            answer_text = "(LLM error: response timed out)"
        except Exception as e:
            logger.exception("llm_failed", error=str(e))
            answer_text = f"(LLM error: {e})"

        sources = chunks_to_meta(chunks)
        ts_refs_meta = refs_to_meta(extract_timestamp_refs(answer_text), file_ids)
        ai_msg = MessageModel.doc(
            conv_id, user_id, "assistant", answer_text,
            source_chunks=sources, timestamp_refs=ts_refs_meta,
        )
        ai_msg_id = await MessageModel.insert(ai_msg)
        await ConversationModel.bump(conv_id, increment_messages=2)
        ai_msg["_id"] = ai_msg_id
        return MessageModel.to_public(ai_msg), {"user_message_id": user_msg_id}

    # ---- SSE streaming ----
    async def stream_answer(
        self, conv_id: str, user_id: str, question: str
    ) -> AsyncIterator[dict[str, Any]]:
        """Yields SSE-friendly dicts: {event, data}. Final event saves message."""
        file_ids, chunks, context_str, history_str = await self._gather_inputs(
            conv_id, user_id, question
        )

        user_msg_id = await MessageModel.insert(
            MessageModel.doc(conv_id, user_id, "user", question)
        )
        yield {"event": "user_message", "data": {"user_message_id": user_msg_id}}

        sources = chunks_to_meta(chunks)
        yield {"event": "sources", "data": {"chunks": sources}}

        messages = build_messages(question, context_str, history_str)

        full_text = ""
        try:
            stream = stream_chat_completion(messages)
            while True:
                try:
                    token = await asyncio.wait_for(
                        anext(stream),
                        timeout=settings.LLM_GENERATION_TIMEOUT_SECONDS,
                    )
                except StopAsyncIteration:
                    break
                if token:
                    full_text += token
                    yield {"event": "token", "data": {"text": token}}
        except TimeoutError:
            logger.exception("stream_timeout")
            yield {"event": "error", "data": {"message": "LLM response timed out"}}
            return
        except Exception as e:
            logger.exception("stream_failed", error=str(e))
            yield {"event": "error", "data": {"message": str(e)}}
            return

        ts_refs_meta = refs_to_meta(extract_timestamp_refs(full_text), file_ids)
        ai_msg_id = await MessageModel.insert(
            MessageModel.doc(
                conv_id, user_id, "assistant", full_text,
                source_chunks=sources, timestamp_refs=ts_refs_meta,
            )
        )
        await ConversationModel.bump(conv_id, increment_messages=2)
        yield {
            "event": "done",
            "data": {
                "message_id": ai_msg_id,
                "timestamp_refs": ts_refs_meta,
                "content": full_text,
            },
        }


chat_service = ChatService()
