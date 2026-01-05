from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_role
from app.database import get_db
from app.enums import UserRole
from app.models import Availability, AvailabilityPattern, User
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityPatternCreate,
    AvailabilityPatternResponse,
    AvailabilityPatternUpdate,
    AvailabilityResponse,
    AvailabilityUpdate,
    AvailabilityWithUser,
    BulkAvailabilityCreate,
)

router = APIRouter(prefix="/availability", tags=["availability"])


# ============ Date-specific Availability ============


@router.post("/", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
async def set_availability(
    availability: AvailabilityCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Availability:
    """Set availability for a specific date. Creates or updates existing entry."""
    # Check if entry already exists for this user and date
    result = await db.execute(
        select(Availability).where(
            and_(
                Availability.user_id == current_user.id,
                Availability.date == availability.date,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing entry
        existing.status = availability.status.value
        existing.note = availability.note
        await db.commit()
        await db.refresh(existing)
        return existing

    # Create new entry
    db_availability = Availability(
        user_id=current_user.id,
        date=availability.date,
        status=availability.status.value,
        note=availability.note,
    )
    db.add(db_availability)
    await db.commit()
    await db.refresh(db_availability)
    return db_availability


@router.post("/bulk", response_model=list[AvailabilityResponse])
async def set_bulk_availability(
    bulk: BulkAvailabilityCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Availability]:
    """Set availability for multiple dates at once."""
    results = []
    for entry in bulk.entries:
        # Check if entry already exists
        result = await db.execute(
            select(Availability).where(
                and_(
                    Availability.user_id == current_user.id,
                    Availability.date == entry.date,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.status = entry.status.value
            existing.note = entry.note
            results.append(existing)
        else:
            db_availability = Availability(
                user_id=current_user.id,
                date=entry.date,
                status=entry.status.value,
                note=entry.note,
            )
            db.add(db_availability)
            results.append(db_availability)

    await db.commit()
    for r in results:
        await db.refresh(r)
    return results


@router.get("/me", response_model=list[AvailabilityResponse])
async def get_my_availability(
    start_date: Annotated[date, Query()],
    end_date: Annotated[date, Query()],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Availability]:
    """Get current user's availability for a date range."""
    result = await db.execute(
        select(Availability)
        .where(
            and_(
                Availability.user_id == current_user.id,
                Availability.date >= start_date,
                Availability.date <= end_date,
            )
        )
        .order_by(Availability.date)
    )
    return list(result.scalars().all())


@router.get("/team", response_model=list[AvailabilityWithUser])
async def get_team_availability(
    start_date: Annotated[date, Query()],
    end_date: Annotated[date, Query()],
    current_user: Annotated[
        User, Depends(require_role(UserRole.ADMIN, UserRole.LEADER))
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict]:
    """Get team availability for a date range (admin/leader only)."""
    result = await db.execute(
        select(Availability, User)
        .join(User, Availability.user_id == User.id)
        .where(
            and_(
                Availability.date >= start_date,
                Availability.date <= end_date,
                User.is_active == True,
            )
        )
        .order_by(Availability.date, User.name)
    )
    rows = result.all()

    return [
        {
            "id": avail.id,
            "user_id": avail.user_id,
            "date": avail.date,
            "status": avail.status,
            "note": avail.note,
            "created_at": avail.created_at,
            "updated_at": avail.updated_at,
            "user_name": user.name,
            "user_email": user.email,
        }
        for avail, user in rows
    ]


@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_availability(
    availability_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an availability entry."""
    result = await db.execute(
        select(Availability).where(Availability.id == availability_id)
    )
    availability = result.scalar_one_or_none()

    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability not found",
        )

    # Only allow deleting own availability (or admin can delete any)
    if (
        availability.user_id != current_user.id
        and current_user.role != UserRole.ADMIN.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's availability",
        )

    await db.delete(availability)
    await db.commit()


# ============ Availability Patterns ============


@router.post(
    "/patterns",
    response_model=AvailabilityPatternResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_pattern(
    pattern: AvailabilityPatternCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AvailabilityPattern:
    """Create a recurring availability pattern."""
    db_pattern = AvailabilityPattern(
        user_id=current_user.id,
        pattern_type=pattern.pattern_type.value,
        day_of_week=pattern.day_of_week,
        status=pattern.status.value,
        start_date=pattern.start_date,
        end_date=pattern.end_date,
        note=pattern.note,
    )
    db.add(db_pattern)
    await db.commit()
    await db.refresh(db_pattern)
    return db_pattern


@router.get("/patterns", response_model=list[AvailabilityPatternResponse])
async def get_my_patterns(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AvailabilityPattern]:
    """Get current user's availability patterns."""
    result = await db.execute(
        select(AvailabilityPattern)
        .where(AvailabilityPattern.user_id == current_user.id)
        .order_by(AvailabilityPattern.day_of_week)
    )
    return list(result.scalars().all())


@router.put("/patterns/{pattern_id}", response_model=AvailabilityPatternResponse)
async def update_pattern(
    pattern_id: UUID,
    pattern_update: AvailabilityPatternUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AvailabilityPattern:
    """Update an availability pattern."""
    result = await db.execute(
        select(AvailabilityPattern).where(AvailabilityPattern.id == pattern_id)
    )
    pattern = result.scalar_one_or_none()

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern not found",
        )

    if pattern.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update another user's pattern",
        )

    update_data = pattern_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):  # Handle enums
            value = value.value
        setattr(pattern, field, value)

    await db.commit()
    await db.refresh(pattern)
    return pattern


@router.delete("/patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pattern(
    pattern_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an availability pattern."""
    result = await db.execute(
        select(AvailabilityPattern).where(AvailabilityPattern.id == pattern_id)
    )
    pattern = result.scalar_one_or_none()

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern not found",
        )

    if pattern.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's pattern",
        )

    await db.delete(pattern)
    await db.commit()
