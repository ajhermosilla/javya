from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.enums import Key, Mood, Theme


class SongBase(BaseModel):
    """Base schema for Song with common fields."""

    title: str = Field(..., min_length=1, max_length=255)
    artist: str | None = Field(None, max_length=255)
    lyrics: str | None = None
    chordpro: str | None = None
    original_key: Key | None = None
    tempo: int | None = Field(None, ge=20, le=300)
    time_signature: str | None = Field(None, max_length=10)
    mood: Mood | None = None
    themes: list[Theme] | None = None
    ccli_number: str | None = Field(None, max_length=50)
    youtube_url: str | None = Field(None, max_length=500)
    notes: str | None = None
    language: str = Field("en", max_length=10)


class SongCreate(SongBase):
    """Schema for creating a new song."""

    pass


class SongUpdate(BaseModel):
    """Schema for updating a song. All fields are optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    artist: str | None = Field(None, max_length=255)
    lyrics: str | None = None
    chordpro: str | None = None
    original_key: Key | None = None
    tempo: int | None = Field(None, ge=20, le=300)
    time_signature: str | None = Field(None, max_length=10)
    mood: Mood | None = None
    themes: list[Theme] | None = None
    ccli_number: str | None = Field(None, max_length=50)
    youtube_url: str | None = Field(None, max_length=500)
    notes: str | None = None
    language: str | None = Field(None, max_length=10)


class SongResponse(SongBase):
    """Schema for song response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
