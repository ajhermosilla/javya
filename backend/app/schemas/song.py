from datetime import datetime
from uuid import UUID

from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import MusicalKey, Mood, Theme


class SongBase(BaseModel):
    """Base schema for Song with common fields."""

    name: str = Field(..., min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def name_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()

    artist: str | None = Field(None, max_length=255)
    url: str | None = Field(None, max_length=500)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must start with http:// or https://")
        if not parsed.netloc:
            raise ValueError("Invalid URL format")
        return v

    original_key: MusicalKey | None = None
    preferred_key: MusicalKey | None = None
    tempo_bpm: int | None = Field(None, ge=20, le=300)
    mood: Mood | None = None
    themes: list[Theme] | None = None
    lyrics: str | None = None
    chordpro_chart: str | None = None
    min_band: list[str] | None = None
    notes: str | None = None


class SongCreate(SongBase):
    """Schema for creating a new song."""

    pass


class SongUpdate(SongBase):
    """Schema for updating a song (PUT - all fields required except name can be null)."""

    pass


class SongResponse(SongBase):
    """Schema for song response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
