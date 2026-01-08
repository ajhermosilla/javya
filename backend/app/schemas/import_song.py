"""Schemas for song import endpoints."""

from pydantic import BaseModel

from app.schemas.song import SongCreate, SongResponse


class ParsedSong(BaseModel):
    """A single parsed song from import preview."""

    file_name: str
    detected_format: str
    success: bool
    error: str | None = None
    song_data: SongCreate | None = None


class ImportPreviewResponse(BaseModel):
    """Response from import preview endpoint."""

    total_files: int
    successful: int
    failed: int
    songs: list[ParsedSong]


class ImportConfirmRequest(BaseModel):
    """Request to save selected songs from preview."""

    songs: list[SongCreate]


class ImportConfirmResponse(BaseModel):
    """Response after saving imported songs."""

    saved_count: int
    songs: list[SongResponse]
