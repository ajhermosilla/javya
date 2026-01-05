from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import EventType
from app.schemas.song import SongResponse


class SetlistSongBase(BaseModel):
    """Base schema for a song in a setlist."""

    song_id: UUID
    position: int = Field(default=0, ge=0)
    notes: str | None = None


class SetlistSongCreate(SetlistSongBase):
    """Schema for adding a song to a setlist."""

    pass


class SetlistSongResponse(SetlistSongBase):
    """Schema for setlist song response with full song data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    song: SongResponse


class SetlistBase(BaseModel):
    """Base schema for Setlist with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    service_date: date | None = None
    event_type: EventType | None = None

    @field_validator("name")
    @classmethod
    def name_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()


class SetlistCreate(SetlistBase):
    """Schema for creating a new setlist."""

    songs: list[SetlistSongCreate] | None = None


class SetlistUpdate(SetlistBase):
    """Schema for updating a setlist."""

    songs: list[SetlistSongCreate] | None = None


class SetlistResponse(SetlistBase):
    """Schema for setlist response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    song_count: int = 0
    created_at: datetime
    updated_at: datetime


class SetlistDetailResponse(SetlistResponse):
    """Schema for setlist response with songs included."""

    songs: list[SetlistSongResponse] = []
