from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums import MusicalKey, Mood, Theme


class SongBase(BaseModel):
    """Base schema for Song with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    artist: str | None = Field(None, max_length=255)
    url: str | None = Field(None, max_length=500)
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
