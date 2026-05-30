"""Chat endpoints: conversations, messages, and SSE streaming."""
from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Query, status
from sse_starlette.sse import EventSourceResponse

from app.middleware.auth import get_current_user_id
from app.schemas.chat import (
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
    MessageCreate,
    MessagePublic,
)
from app.schemas.common import MessageResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/conversations",
    response_model=ConversationPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreate,
    user_id: str = Depends(get_current_user_id),
) -> ConversationPublic:
    doc = await chat_service.create_conversation(user_id, payload.title, payload.file_ids)
    return ConversationPublic.model_validate(doc)


@router.get("/conversations", response_model=list[ConversationPublic])
async def list_conversations(
    favorites: bool = Query(False),
    user_id: str = Depends(get_current_user_id),
) -> list[ConversationPublic]:
    docs = await chat_service.list_conversations(user_id, only_favorites=favorites)
    return [ConversationPublic.model_validate(d) for d in docs]


@router.get("/conversations/{conv_id}", response_model=ConversationPublic)
async def get_conversation(
    conv_id: str, user_id: str = Depends(get_current_user_id)
) -> ConversationPublic:
    doc = await chat_service.get_conversation(conv_id, user_id)
    return ConversationPublic.model_validate(doc)


@router.patch("/conversations/{conv_id}", response_model=ConversationPublic)
async def update_conversation(
    conv_id: str,
    payload: ConversationUpdate,
    user_id: str = Depends(get_current_user_id),
) -> ConversationPublic:
    doc = await chat_service.update_conversation(
        conv_id,
        user_id,
        title=payload.title,
        is_favorite=payload.is_favorite,
        file_ids=payload.file_ids,
    )
    return ConversationPublic.model_validate(doc)


@router.delete("/conversations/{conv_id}", response_model=MessageResponse)
async def delete_conversation(
    conv_id: str, user_id: str = Depends(get_current_user_id)
) -> MessageResponse:
    await chat_service.delete_conversation(conv_id, user_id)
    return MessageResponse(message="Conversation deleted.")


@router.get(
    "/conversations/{conv_id}/messages",
    response_model=list[MessagePublic],
)
async def list_messages(
    conv_id: str, user_id: str = Depends(get_current_user_id)
) -> list[MessagePublic]:
    docs = await chat_service.list_messages(conv_id, user_id)
    return [MessagePublic.model_validate(d) for d in docs]


@router.post(
    "/conversations/{conv_id}/messages",
    response_model=MessagePublic,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    conv_id: str,
    payload: MessageCreate,
    user_id: str = Depends(get_current_user_id),
) -> MessagePublic:
    ai_msg, _ = await chat_service.answer(conv_id, user_id, payload.content)
    return MessagePublic.model_validate(ai_msg)


@router.get("/conversations/{conv_id}/messages/stream")
async def stream_message(
    conv_id: str,
    q: str = Query(..., min_length=1, max_length=8000),
    user_id: str = Depends(get_current_user_id),
):
    """SSE streaming of an AI response.

    Frontend usage (EventSource):
        new EventSource('/api/v1/chat/conversations/{id}/messages/stream?q=...&token=...')
    """

    async def event_gen() -> AsyncIterator[dict]:
        try:
            async for chunk in chat_service.stream_answer(conv_id, user_id, q):
                yield {
                    "event": chunk["event"],
                    "data": json.dumps(chunk["data"], default=str),
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield {
                "event": "error",
                "data": json.dumps({"message": f"Server error: {e}"}),
            }

    return EventSourceResponse(event_gen(), ping=15)
