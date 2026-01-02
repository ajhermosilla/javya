from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.enums import MusicalKey, Mood, Theme
from app.models.song import Song
from app.schemas.song import SongCreate, SongResponse, SongUpdate

router = APIRouter()


@router.post("/", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
async def create_song(
    song_data: SongCreate,
    db: AsyncSession = Depends(get_db),
) -> Song:
    """Create a new song."""
    song = Song(
        name=song_data.name,
        artist=song_data.artist,
        url=song_data.url,
        original_key=song_data.original_key.value if song_data.original_key else None,
        preferred_key=song_data.preferred_key.value if song_data.preferred_key else None,
        tempo_bpm=song_data.tempo_bpm,
        mood=song_data.mood.value if song_data.mood else None,
        themes=[t.value for t in song_data.themes] if song_data.themes else None,
        lyrics=song_data.lyrics,
        chordpro_chart=song_data.chordpro_chart,
        min_band=song_data.min_band,
        notes=song_data.notes,
    )
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song


@router.get("/", response_model=list[SongResponse])
async def list_songs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, description="Search in name and artist"),
    key: MusicalKey | None = Query(None, description="Filter by key"),
    mood: Mood | None = Query(None, description="Filter by mood"),
    theme: Theme | None = Query(None, description="Filter by theme"),
    db: AsyncSession = Depends(get_db),
) -> list[Song]:
    """List all songs with optional filtering."""
    query = select(Song)

    if search:
        query = query.where(
            Song.name.ilike(f"%{search}%") | Song.artist.ilike(f"%{search}%")
        )

    if key:
        query = query.where(
            (Song.original_key == key.value) | (Song.preferred_key == key.value)
        )

    if mood:
        query = query.where(Song.mood == mood.value)

    if theme:
        query = query.where(Song.themes.contains([theme.value]))

    query = query.order_by(Song.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Song:
    """Get a song by ID."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )

    return song


@router.put("/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: UUID,
    song_data: SongUpdate,
    db: AsyncSession = Depends(get_db),
) -> Song:
    """Update a song by ID."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )

    # Update all fields
    song.name = song_data.name
    song.artist = song_data.artist
    song.url = song_data.url
    song.original_key = song_data.original_key.value if song_data.original_key else None
    song.preferred_key = song_data.preferred_key.value if song_data.preferred_key else None
    song.tempo_bpm = song_data.tempo_bpm
    song.mood = song_data.mood.value if song_data.mood else None
    song.themes = [t.value for t in song_data.themes] if song_data.themes else None
    song.lyrics = song_data.lyrics
    song.chordpro_chart = song_data.chordpro_chart
    song.min_band = song_data.min_band
    song.notes = song_data.notes

    await db.commit()
    await db.refresh(song)
    return song


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(
    song_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a song by ID."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )

    await db.delete(song)
    await db.commit()
