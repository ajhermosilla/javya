from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.enums import ServiceRole, AvailabilityStatus


class SetlistAssignmentBase(BaseModel):
    """Base schema for setlist assignment."""

    user_id: UUID
    service_role: ServiceRole
    notes: str | None = Field(None, max_length=500)


class SetlistAssignmentCreate(SetlistAssignmentBase):
    """Schema for creating a setlist assignment."""

    pass


class SetlistAssignmentUpdate(BaseModel):
    """Schema for updating a setlist assignment."""

    service_role: ServiceRole | None = None
    notes: str | None = Field(None, max_length=500)


class SetlistAssignmentResponse(BaseModel):
    """Schema for setlist assignment response."""

    id: UUID
    setlist_id: UUID
    user_id: UUID
    service_role: ServiceRole
    notes: str | None
    confirmed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SetlistAssignmentWithUser(SetlistAssignmentResponse):
    """Assignment with user info for display."""

    user_name: str
    user_email: str
    user_role: str
    availability_status: AvailabilityStatus | None = None


class SetlistAssignmentConfirm(BaseModel):
    """Schema for confirming an assignment."""

    confirmed: bool = True


# Scheduling query responses
class TeamMemberAvailability(BaseModel):
    """Team member with availability for a specific date."""

    user_id: UUID
    user_name: str
    user_email: str
    user_role: str
    availability_status: AvailabilityStatus | None = None
    availability_note: str | None = None


class MyAssignmentResponse(BaseModel):
    """User's own assignment with setlist info."""

    id: UUID
    service_role: ServiceRole
    notes: str | None
    confirmed: bool
    setlist_id: UUID
    setlist_name: str
    service_date: str | None
    event_type: str | None
