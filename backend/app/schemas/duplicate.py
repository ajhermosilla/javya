"""Schemas for duplicate song detection."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums import MusicalKey


class SongCheck(BaseModel):
    """Song data to check for duplicates."""

    name: str = Field(..., min_length=1, max_length=255)
    artist: str | None = Field(None, max_length=255)


class ExistingSongSummary(BaseModel):
    """Summary of an existing song (for duplicate responses)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    artist: str | None = None
    original_key: MusicalKey | None = None


class DuplicateMatch(BaseModel):
    """A duplicate match result."""

    index: int
    name: str
    artist: str | None = None
    existing_song: ExistingSongSummary


class CheckDuplicatesRequest(BaseModel):
    """Request to check for duplicate songs."""

    songs: list[SongCheck] = Field(..., min_length=1, max_length=100)


class CheckDuplicatesResponse(BaseModel):
    """Response with duplicate matches."""

    duplicates: list[DuplicateMatch]
