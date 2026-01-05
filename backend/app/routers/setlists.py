import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.enums import EventType
from app.models.setlist import Setlist
from app.models.setlist_song import SetlistSong
from app.schemas.setlist import (
    SetlistCreate,
    SetlistUpdate,
    SetlistResponse,
    SetlistDetailResponse,
)
from app.services.export_freeshow import generate_freeshow_project
from app.services.export_quelea import generate_quelea_schedule

router = APIRouter()


def sanitize_filename(name: str, fallback_id: UUID) -> str:
    """Create a safe filename from a name, using ID as fallback for uniqueness."""
    safe_name = "".join(c for c in name if c.isalnum() or c in " -_").strip()
    if not safe_name:
        # Use first 8 chars of UUID for uniqueness
        safe_name = f"setlist-{str(fallback_id)[:8]}"
    return safe_name


@router.post("/", response_model=SetlistDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_setlist(
    setlist_data: SetlistCreate,
    db: AsyncSession = Depends(get_db),
) -> Setlist:
    """Create a new setlist with optional songs."""
    setlist = Setlist(
        name=setlist_data.name,
        description=setlist_data.description,
        service_date=setlist_data.service_date,
        event_type=setlist_data.event_type.value if setlist_data.event_type else None,
    )
    db.add(setlist)
    await db.flush()  # Get the setlist ID

    # Add songs if provided
    if setlist_data.songs:
        for song_data in setlist_data.songs:
            setlist_song = SetlistSong(
                setlist_id=setlist.id,
                song_id=song_data.song_id,
                position=song_data.position,
                notes=song_data.notes,
            )
            db.add(setlist_song)

    await db.commit()

    # Reload with songs
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.songs).selectinload(SetlistSong.song))
        .where(Setlist.id == setlist.id)
    )
    return result.scalar_one()


@router.get("/", response_model=list[SetlistResponse])
async def list_setlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, description="Search in name"),
    event_type: EventType | None = Query(None, description="Filter by event type"),
    db: AsyncSession = Depends(get_db),
) -> list[Setlist]:
    """List all setlists with optional filtering."""
    query = select(Setlist)

    if search:
        query = query.where(Setlist.name.ilike(f"%{search}%"))

    if event_type:
        query = query.where(Setlist.event_type == event_type.value)

    query = query.order_by(Setlist.service_date.desc().nulls_last(), Setlist.name)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{setlist_id}", response_model=SetlistDetailResponse)
async def get_setlist(
    setlist_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Setlist:
    """Get a setlist by ID with all songs."""
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.songs).selectinload(SetlistSong.song))
        .where(Setlist.id == setlist_id)
    )
    setlist = result.scalar_one_or_none()

    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    return setlist


@router.put("/{setlist_id}", response_model=SetlistDetailResponse)
async def update_setlist(
    setlist_id: UUID,
    setlist_data: SetlistUpdate,
    db: AsyncSession = Depends(get_db),
) -> Setlist:
    """Update a setlist by ID, including replacing songs."""
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.songs))
        .where(Setlist.id == setlist_id)
    )
    setlist = result.scalar_one_or_none()

    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    # Update metadata
    setlist.name = setlist_data.name
    setlist.description = setlist_data.description
    setlist.service_date = setlist_data.service_date
    setlist.event_type = setlist_data.event_type.value if setlist_data.event_type else None

    # Replace songs if provided
    if setlist_data.songs is not None:
        # Clear existing songs
        for existing_song in setlist.songs:
            await db.delete(existing_song)

        # Add new songs
        for song_data in setlist_data.songs:
            setlist_song = SetlistSong(
                setlist_id=setlist.id,
                song_id=song_data.song_id,
                position=song_data.position,
                notes=song_data.notes,
            )
            db.add(setlist_song)

    await db.commit()

    # Reload with songs
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.songs).selectinload(SetlistSong.song))
        .where(Setlist.id == setlist_id)
    )
    return result.scalar_one()


@router.delete("/{setlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setlist(
    setlist_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a setlist by ID (songs are cascade deleted)."""
    result = await db.execute(select(Setlist).where(Setlist.id == setlist_id))
    setlist = result.scalar_one_or_none()

    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    await db.delete(setlist)
    await db.commit()


@router.get("/{setlist_id}/export/freeshow")
async def export_setlist_freeshow(
    setlist_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Export a setlist to FreeShow .show format."""
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.songs).selectinload(SetlistSong.song))
        .where(Setlist.id == setlist_id)
    )
    setlist = result.scalar_one_or_none()

    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    # Generate FreeShow project
    freeshow_data = generate_freeshow_project(setlist)

    # Create filename from setlist name
    filename = f"{sanitize_filename(setlist.name, setlist.id)}.project"

    return Response(
        content=json.dumps(freeshow_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.get("/{setlist_id}/export/quelea")
async def export_setlist_quelea(
    setlist_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Export a setlist to Quelea .qsch schedule format."""
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.songs).selectinload(SetlistSong.song))
        .where(Setlist.id == setlist_id)
    )
    setlist = result.scalar_one_or_none()

    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    # Generate Quelea schedule ZIP
    quelea_data = generate_quelea_schedule(setlist)

    # Create filename from setlist name
    filename = f"{sanitize_filename(setlist.name, setlist.id)}.qsch"

    return Response(
        content=quelea_data,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
