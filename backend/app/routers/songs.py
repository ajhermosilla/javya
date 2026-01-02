from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.enums import Mood, Theme
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
        title=song_data.title,
        artist=song_data.artist,
        lyrics=song_data.lyrics,
        chordpro=song_data.chordpro,
        original_key=song_data.original_key.value if song_data.original_key else None,
        tempo=song_data.tempo,
        time_signature=song_data.time_signature,
        mood=song_data.mood.value if song_data.mood else None,
        themes=[t.value for t in song_data.themes] if song_data.themes else None,
        ccli_number=song_data.ccli_number,
        youtube_url=song_data.youtube_url,
        notes=song_data.notes,
        language=song_data.language,
    )
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song


@router.get("/", response_model=list[SongResponse])
async def list_songs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, description="Search in title and artist"),
    mood: Mood | None = Query(None, description="Filter by mood"),
    theme: Theme | None = Query(None, description="Filter by theme"),
    language: str | None = Query(None, max_length=10, description="Filter by language"),
    db: AsyncSession = Depends(get_db),
) -> list[Song]:
    """List all songs with optional filtering."""
    query = select(Song)

    if search:
        query = query.where(
            Song.title.ilike(f"%{search}%") | Song.artist.ilike(f"%{search}%")
        )

    if mood:
        query = query.where(Song.mood == mood.value)

    if theme:
        query = query.where(Song.themes.contains([theme.value]))

    if language:
        query = query.where(Song.language == language)

    query = query.order_by(Song.title).offset(skip).limit(limit)
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


@router.patch("/{song_id}", response_model=SongResponse)
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

    update_data = song_data.model_dump(exclude_unset=True)

    # Handle enum conversions
    if "original_key" in update_data and update_data["original_key"]:
        update_data["original_key"] = update_data["original_key"].value
    if "mood" in update_data and update_data["mood"]:
        update_data["mood"] = update_data["mood"].value
    if "themes" in update_data and update_data["themes"]:
        update_data["themes"] = [t.value for t in update_data["themes"]]

    for field, value in update_data.items():
        setattr(song, field, value)

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
