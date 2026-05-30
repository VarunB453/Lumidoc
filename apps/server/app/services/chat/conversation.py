"""Conversation CRUD with ownership checks (split from chat_service)."""
from __future__ import annotations

from typing import Any

from app.core.exceptions import NotFoundError
from app.models.conversation import ConversationModel
from app.models.file import FileModel
from app.models.message import MessageModel


async def _validate_file_ownership(file_ids: list[str], user_id: str) -> None:
    for fid in file_ids:
        if not await FileModel.find_by_id(fid, user_id):
            raise NotFoundError(f"File {fid} not found or not owned by user.")


async def create(user_id: str, title: str | None, file_ids: list[str]) -> dict[str, Any]:
    await _validate_file_ownership(file_ids, user_id)
    title = title or "New conversation"
    conv_doc = ConversationModel.doc(user_id=user_id, title=title, file_ids=file_ids)
    conv_id = await ConversationModel.insert(conv_doc)
    fresh = await ConversationModel.find_by_id(conv_id, user_id)
    return ConversationModel.to_public(fresh)


async def list_for_user(
    user_id: str, only_favorites: bool = False
) -> list[dict[str, Any]]:
    docs = await ConversationModel.list_for_user(user_id, only_favorites=only_favorites)
    return [ConversationModel.to_public(d) for d in docs]


async def update(
    conv_id: str,
    user_id: str,
    *,
    title: str | None = None,
    is_favorite: bool | None = None,
    file_ids: list[str] | None = None,
) -> dict[str, Any]:
    if not await ConversationModel.find_by_id(conv_id, user_id):
        raise NotFoundError("Conversation not found.")
    fields: dict[str, Any] = {}
    if title is not None:
        fields["title"] = title.strip() or "New conversation"
    if is_favorite is not None:
        fields["is_favorite"] = bool(is_favorite)
    if file_ids is not None:
        await _validate_file_ownership(file_ids, user_id)
        fields["file_ids"] = file_ids
    updated = await ConversationModel.update_fields(conv_id, user_id, fields)
    if not updated:
        raise NotFoundError("Conversation not found.")
    return ConversationModel.to_public(updated)


async def delete(conv_id: str, user_id: str) -> None:
    if not await ConversationModel.soft_delete(conv_id, user_id):
        raise NotFoundError("Conversation not found.")


async def get(conv_id: str, user_id: str) -> dict[str, Any]:
    doc = await ConversationModel.find_by_id(conv_id, user_id)
    if not doc:
        raise NotFoundError("Conversation not found.")
    return ConversationModel.to_public(doc)


async def list_messages(conv_id: str, user_id: str) -> list[dict[str, Any]]:
    await get(conv_id, user_id)  # ownership check
    docs = await MessageModel.list_for_conversation(conv_id)
    return [MessageModel.to_public(d) for d in docs]
