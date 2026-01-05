from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_active_user, require_role
from app.database import get_db
from app.enums import UserRole
from app.models.availability import Availability
from app.models.setlist import Setlist
from app.models.setlist_assignment import SetlistAssignment
from app.models.user import User
from app.schemas.setlist_assignment import (
    TeamMemberAvailability,
    MyAssignmentResponse,
)

router = APIRouter()


@router.get("/calendar")
async def get_calendar(
    start_date: date = Query(..., description="Start date for calendar range"),
    end_date: date = Query(..., description="End date for calendar range"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Get setlists with assignments for a date range (for calendar view)."""
    result = await db.execute(
        select(Setlist)
        .options(
            selectinload(Setlist.assignments).selectinload(SetlistAssignment.user)
        )
        .where(
            and_(
                Setlist.service_date >= start_date,
                Setlist.service_date <= end_date,
            )
        )
        .order_by(Setlist.service_date)
    )
    setlists = result.scalars().all()

    return [
        {
            "id": str(setlist.id),
            "name": setlist.name,
            "service_date": setlist.service_date.isoformat() if setlist.service_date else None,
            "event_type": setlist.event_type,
            "song_count": setlist.song_count,
            "assignments": [
                {
                    "id": str(a.id),
                    "user_id": str(a.user_id),
                    "user_name": a.user.name,
                    "service_role": a.service_role,
                    "confirmed": a.confirmed,
                }
                for a in setlist.assignments
            ],
        }
        for setlist in setlists
    ]


@router.get("/availability", response_model=list[TeamMemberAvailability])
async def check_team_availability(
    service_date: date = Query(..., description="Date to check availability for"),
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.LEADER))] = None,
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberAvailability]:
    """Get all team members with their availability for a specific date (admin/leader only)."""
    # Get all active users with their availability for the date
    result = await db.execute(
        select(User, Availability)
        .outerjoin(
            Availability,
            and_(
                Availability.user_id == User.id,
                Availability.date == service_date,
            )
        )
        .where(User.is_active == True)
        .order_by(User.name)
    )
    rows = result.all()

    return [
        TeamMemberAvailability(
            user_id=user.id,
            user_name=user.name,
            user_email=user.email,
            user_role=user.role,
            availability_status=avail.status if avail else None,
            availability_note=avail.note if avail else None,
        )
        for user, avail in rows
    ]


@router.get("/my-assignments", response_model=list[MyAssignmentResponse])
async def get_my_assignments(
    upcoming_only: bool = Query(True, description="Only show upcoming assignments"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> list[MyAssignmentResponse]:
    """Get current user's assignments."""
    query = (
        select(SetlistAssignment, Setlist)
        .join(Setlist, SetlistAssignment.setlist_id == Setlist.id)
        .where(SetlistAssignment.user_id == current_user.id)
    )

    if upcoming_only:
        today = date.today()
        query = query.where(Setlist.service_date >= today)

    query = query.order_by(Setlist.service_date.asc().nulls_last())
    result = await db.execute(query)
    rows = result.all()

    return [
        MyAssignmentResponse(
            id=assignment.id,
            service_role=assignment.service_role,
            notes=assignment.notes,
            confirmed=assignment.confirmed,
            setlist_id=setlist.id,
            setlist_name=setlist.name,
            service_date=setlist.service_date.isoformat() if setlist.service_date else None,
            event_type=setlist.event_type,
        )
        for assignment, setlist in rows
    ]
