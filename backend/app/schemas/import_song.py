"""Schemas for song import endpoints."""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from app.enums import MusicalKey
from app.schemas.duplicate import ExistingSongSummary
from app.schemas.song import SongCreate, SongResponse


class ImportAction(str, Enum):
    """Action to take for an imported song."""

    CREATE = "create"  # Create as new song
    MERGE = "merge"  # Merge with existing song
    SKIP = "skip"  # Don't import


class SongImportItem(BaseModel):
    """A song to import with action specification."""

    song_data: SongCreate
    action: ImportAction = ImportAction.CREATE
    existing_song_id: UUID | None = None  # Required when action is MERGE


class UrlImportRequest(BaseModel):
    """Request to import a song from a URL."""

    url: HttpUrl


class ParsedSong(BaseModel):
    """A single parsed song from import preview."""

    file_name: str
    detected_format: str
    success: bool
    error: str | None = None
    song_data: SongCreate | None = None
    duplicate: ExistingSongSummary | None = None

    # Key detection results
    specified_key: MusicalKey | None = None  # From file metadata
    detected_key: MusicalKey | None = None  # From chord analysis
    key_confidence: str | None = None  # "high", "medium", "low"

    # Section detection results
    sections_normalized: bool = False  # Whether markers were normalized


class ImportPreviewResponse(BaseModel):
    """Response from import preview endpoint."""

    total_files: int
    successful: int
    failed: int
    songs: list[ParsedSong]


class ImportConfirmRequest(BaseModel):
    """Request to save selected songs from preview."""

    songs: list[SongImportItem]


class ImportConfirmResponse(BaseModel):
    """Response after saving imported songs."""

    created_count: int
    merged_count: int
    skipped_count: int
    songs: list[SongResponse]
