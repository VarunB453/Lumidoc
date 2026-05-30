"""User-related Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import ORMModel


class UserRegister(ORMModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=120)

    @field_validator("password")
    @classmethod
    def _strong(cls, v: str) -> str:
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain letters and digits.")
        return v


class UserLogin(ORMModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserPublic(ORMModel):
    id: str
    email: EmailStr
    name: str
    avatar_url: str | None = None
    role: Literal["user", "admin"] = "user"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime | None = None


class TokenPair(ORMModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expiry


class RefreshRequest(ORMModel):
    refresh_token: str = Field(..., min_length=10)


class LogoutRequest(ORMModel):
    refresh_token: str = Field(..., min_length=10)


# ----- profile / avatar / password (moved out of endpoints/users.py) -----
class ProfileUpdate(ORMModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    email: EmailStr | None = None


class PasswordChange(ORMModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class AvatarResponse(ORMModel):
    avatar_url: str
