import json
from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_active_user, require_role
from app.database import get_db
from app.enums import EventType, ServiceRole, UserRole
from app.models.availability import Availability
from app.models.setlist import Setlist
from app.models.setlist_assignment import SetlistAssignment
from app.models.setlist_song import SetlistSong
from app.models.user import User
from app.schemas.setlist import (
    SetlistCreate,
    SetlistUpdate,
    SetlistResponse,
    SetlistDetailResponse,
)
from app.schemas.setlist_assignment import (
    SetlistAssignmentCreate,
    SetlistAssignmentUpdate,
    SetlistAssignmentWithUser,
    SetlistAssignmentConfirm,
)
from app.services.export_freeshow import generate_freeshow_project
from app.services.export_quelea import generate_quelea_schedule

router = APIRouter()


def escape_like_pattern(value: str) -> str:
    """Escape special LIKE pattern characters to prevent SQL injection."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


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
        escaped_search = escape_like_pattern(search)
        query = query.where(Setlist.name.ilike(f"%{escaped_search}%", escape="\\"))

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

    # Expire cached objects to ensure fresh data on reload
    db.expire_all()

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
    _current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.LEADER))],
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
    current_user: Annotated[User, Depends(get_current_active_user)],
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

    if not setlist.songs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot export an empty setlist. Add songs first.",
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
    current_user: Annotated[User, Depends(get_current_active_user)],
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

    if not setlist.songs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot export an empty setlist. Add songs first.",
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


# ============================================================================
# Assignment Endpoints
# ============================================================================


async def _get_assignment_with_user(
    assignment: SetlistAssignment,
    setlist: Setlist,
    db: AsyncSession,
) -> SetlistAssignmentWithUser:
    """Helper to build assignment response with user info and availability."""
    # Get availability for the service date if exists
    availability_status = None
    if setlist.service_date:
        avail_result = await db.execute(
            select(Availability).where(
                and_(
                    Availability.user_id == assignment.user_id,
                    Availability.date == setlist.service_date,
                )
            )
        )
        avail = avail_result.scalar_one_or_none()
        if avail:
            availability_status = avail.status

    return SetlistAssignmentWithUser(
        id=assignment.id,
        setlist_id=assignment.setlist_id,
        user_id=assignment.user_id,
        service_role=assignment.service_role,
        notes=assignment.notes,
        confirmed=assignment.confirmed,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
        user_name=assignment.user.name,
        user_email=assignment.user.email,
        user_role=assignment.user.role,
        availability_status=availability_status,
    )


@router.get("/{setlist_id}/assignments", response_model=list[SetlistAssignmentWithUser])
async def list_assignments(
    setlist_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
) -> list[SetlistAssignmentWithUser]:
    """List all assignments for a setlist."""
    # Get setlist first to check it exists and get service_date
    setlist_result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id)
    )
    setlist = setlist_result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    # Get assignments with user info
    result = await db.execute(
        select(SetlistAssignment)
        .options(selectinload(SetlistAssignment.user))
        .where(SetlistAssignment.setlist_id == setlist_id)
        .order_by(SetlistAssignment.service_role)
    )
    assignments = result.scalars().all()

    return [
        await _get_assignment_with_user(a, setlist, db)
        for a in assignments
    ]


@router.post(
    "/{setlist_id}/assignments",
    response_model=SetlistAssignmentWithUser,
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    setlist_id: UUID,
    assignment_data: SetlistAssignmentCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.LEADER))],
    db: AsyncSession = Depends(get_db),
) -> SetlistAssignmentWithUser:
    """Create a new assignment for a setlist (admin/leader only)."""
    # Verify setlist exists
    setlist_result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id)
    )
    setlist = setlist_result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    # Verify user exists and is active
    user_result = await db.execute(
        select(User).where(User.id == assignment_data.user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {assignment_data.user_id} not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign inactive user to setlist",
        )

    # Check for duplicate assignment
    existing = await db.execute(
        select(SetlistAssignment).where(
            and_(
                SetlistAssignment.setlist_id == setlist_id,
                SetlistAssignment.user_id == assignment_data.user_id,
                SetlistAssignment.service_role == assignment_data.service_role.value,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already assigned to this role in this setlist",
        )

    assignment = SetlistAssignment(
        setlist_id=setlist_id,
        user_id=assignment_data.user_id,
        service_role=assignment_data.service_role.value,
        notes=assignment_data.notes,
    )
    db.add(assignment)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already assigned to this role in this setlist",
        )

    # Reload with user
    result = await db.execute(
        select(SetlistAssignment)
        .options(selectinload(SetlistAssignment.user))
        .where(SetlistAssignment.id == assignment.id)
    )
    assignment = result.scalar_one()

    return await _get_assignment_with_user(assignment, setlist, db)


@router.put(
    "/{setlist_id}/assignments/{assignment_id}",
    response_model=SetlistAssignmentWithUser,
)
async def update_assignment(
    setlist_id: UUID,
    assignment_id: UUID,
    assignment_data: SetlistAssignmentUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.LEADER))],
    db: AsyncSession = Depends(get_db),
) -> SetlistAssignmentWithUser:
    """Update an assignment (admin/leader only)."""
    # Get setlist for service_date
    setlist_result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id)
    )
    setlist = setlist_result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    # Get assignment
    result = await db.execute(
        select(SetlistAssignment)
        .options(selectinload(SetlistAssignment.user))
        .where(
            and_(
                SetlistAssignment.id == assignment_id,
                SetlistAssignment.setlist_id == setlist_id,
            )
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with id {assignment_id} not found",
        )

    # Update fields
    if assignment_data.service_role is not None:
        assignment.service_role = assignment_data.service_role.value
    if assignment_data.notes is not None:
        assignment.notes = assignment_data.notes

    await db.commit()
    await db.refresh(assignment)

    return await _get_assignment_with_user(assignment, setlist, db)


@router.delete(
    "/{setlist_id}/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_assignment(
    setlist_id: UUID,
    assignment_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.LEADER))],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an assignment (admin/leader only)."""
    result = await db.execute(
        select(SetlistAssignment).where(
            and_(
                SetlistAssignment.id == assignment_id,
                SetlistAssignment.setlist_id == setlist_id,
            )
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with id {assignment_id} not found",
        )

    await db.delete(assignment)
    await db.commit()


@router.patch(
    "/{setlist_id}/assignments/{assignment_id}/confirm",
    response_model=SetlistAssignmentWithUser,
)
async def confirm_assignment(
    setlist_id: UUID,
    assignment_id: UUID,
    confirm_data: SetlistAssignmentConfirm,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
) -> SetlistAssignmentWithUser:
    """Confirm or unconfirm an assignment (only the assigned user can do this)."""
    # Get setlist for service_date
    setlist_result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id)
    )
    setlist = setlist_result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setlist with id {setlist_id} not found",
        )

    # Get assignment
    result = await db.execute(
        select(SetlistAssignment)
        .options(selectinload(SetlistAssignment.user))
        .where(
            and_(
                SetlistAssignment.id == assignment_id,
                SetlistAssignment.setlist_id == setlist_id,
            )
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with id {assignment_id} not found",
        )

    # Only the assigned user can confirm their own assignment
    if assignment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only confirm your own assignments",
        )

    assignment.confirmed = confirm_data.confirmed
    await db.commit()
    await db.refresh(assignment)

    return await _get_assignment_with_user(assignment, setlist, db)
