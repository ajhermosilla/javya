from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.enums import UserRole


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def name_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()


class UserCreate(UserBase):
    """Schema for creating a new user (registration)."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    name: str | None = Field(None, min_length=1, max_length=255)


class UserRoleUpdate(BaseModel):
    """Schema for updating user role (admin only)."""

    role: UserRole


class UserResponse(UserBase):
    """Schema for user response (public info)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: UUID | None = None
