"""Service for detecting duplicate songs."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.song import Song
from app.schemas.duplicate import (
    DuplicateMatch,
    ExistingSongSummary,
    SongCheck,
)


async def find_duplicates(
    db: AsyncSession,
    songs: list[SongCheck],
) -> list[DuplicateMatch]:
    """Find existing songs matching name + artist (case-insensitive).

    Args:
        db: Database session.
        songs: List of songs to check for duplicates.

    Returns:
        List of DuplicateMatch for songs that have existing matches.
    """
    results: list[DuplicateMatch] = []

    for idx, song in enumerate(songs):
        # Case-insensitive match on name
        query = select(Song).where(
            func.lower(Song.name) == func.lower(song.name)
        )

        # Match artist (case-insensitive if provided, or null if not)
        if song.artist:
            query = query.where(
                func.lower(Song.artist) == func.lower(song.artist)
            )
        else:
            # If no artist provided, only match songs with no artist
            query = query.where(Song.artist.is_(None))

        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            results.append(
                DuplicateMatch(
                    index=idx,
                    name=song.name,
                    artist=song.artist,
                    existing_song=ExistingSongSummary.model_validate(existing),
                )
            )

    return results


async def find_single_duplicate(
    db: AsyncSession,
    name: str,
    artist: str | None,
) -> Song | None:
    """Find a single duplicate song by name + artist.

    Args:
        db: Database session.
        name: Song name to check.
        artist: Artist name to check (optional).

    Returns:
        Existing Song if found, None otherwise.
    """
    query = select(Song).where(func.lower(Song.name) == func.lower(name))

    if artist:
        query = query.where(func.lower(Song.artist) == func.lower(artist))
    else:
        query = query.where(Song.artist.is_(None))

    result = await db.execute(query)
    return result.scalar_one_or_none()
