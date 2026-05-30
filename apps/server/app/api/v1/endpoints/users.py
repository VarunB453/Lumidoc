"""User profile endpoints: get current user, update profile, change password,
upload avatar."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.config import settings
from app.core.exceptions import (
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.core.security import hash_password, verify_password
from app.middleware.auth import get_current_user_id
from app.models.user import UserModel
from app.schemas.common import MessageResponse
from app.schemas.user import (
    AvatarResponse,
    PasswordChange,
    ProfileUpdate,
    UserPublic,
)
from app.services.storage_service import storage_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(user_id: str = Depends(get_current_user_id)) -> UserPublic:
    doc = await UserModel.find_by_id(user_id)
    if not doc:
        raise NotFoundError("User not found.")
    return UserPublic.model_validate(UserModel.to_public(doc))


@router.patch("/me", response_model=UserPublic)
async def update_me(
    payload: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
) -> UserPublic:
    doc = await UserModel.find_by_id(user_id)
    if not doc:
        raise NotFoundError("User not found.")

    fields: dict = {}
    if payload.name is not None:
        fields["name"] = payload.name.strip()
    if payload.email is not None and payload.email.lower() != doc["email"]:
        existing = await UserModel.find_by_email(payload.email)
        if existing and str(existing["_id"]) != user_id:
            raise ValidationError("Email is already in use by another account.")
        fields["email"] = payload.email.lower()

    if fields:
        await UserModel.update(user_id, fields)
    fresh = await UserModel.find_by_id(user_id)
    return UserPublic.model_validate(UserModel.to_public(fresh))


@router.post("/me/password", response_model=MessageResponse)
async def change_password(
    payload: PasswordChange,
    user_id: str = Depends(get_current_user_id),
) -> MessageResponse:
    doc = await UserModel.find_by_id(user_id)
    if not doc:
        raise NotFoundError("User not found.")
    if not doc.get("hashed_password"):
        raise ValidationError(
            "This account uses social sign-in. Set a password from the provider."
        )
    if not verify_password(payload.current_password, doc["hashed_password"]):
        raise UnauthorizedError("Current password is incorrect.")
    if not any(c.isalpha() for c in payload.new_password) or not any(
        c.isdigit() for c in payload.new_password
    ):
        raise ValidationError("Password must contain letters and digits.")
    await UserModel.update(user_id, {"hashed_password": hash_password(payload.new_password)})
    return MessageResponse(message="Password updated.")


@router.post("/me/avatar", response_model=AvatarResponse, status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
) -> AvatarResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise ValidationError("Only image uploads are accepted for avatars.")
    data = await file.read()
    if len(data) == 0:
        raise ValidationError("Empty file.")
    if len(data) > 5 * 1024 * 1024:
        raise ValidationError("Avatars must be under 5 MB.")

    suffix = Path(file.filename or "avatar.png").suffix.lower() or ".png"
    filename = f"{int(datetime.now(UTC).timestamp())}{suffix}"
    key = f"users/{user_id}/avatar/{filename}"
    await storage_service.upload_bytes(key, data, content_type=file.content_type)
    # In dev (local storage), avatars are served publicly under /api/v1/avatars/.
    # In prod, fall back to the presigned URL.
    if settings.USE_LOCAL_STORAGE:
        url = f"/api/v1/avatars/{user_id}/{filename}"
    else:
        url = await storage_service.presigned_url(key)
    await UserModel.update(user_id, {"avatar_url": url, "avatar_key": key})
    return AvatarResponse(avatar_url=url)
