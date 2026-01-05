from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.enums import AvailabilityStatus, PatternType


# Availability schemas
class AvailabilityBase(BaseModel):
    """Base schema for availability."""

    date: date
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    note: str | None = Field(None, max_length=500)


class AvailabilityCreate(AvailabilityBase):
    """Schema for creating availability."""

    pass


class AvailabilityUpdate(BaseModel):
    """Schema for updating availability."""

    status: AvailabilityStatus | None = None
    note: str | None = Field(None, max_length=500)


class AvailabilityResponse(AvailabilityBase):
    """Schema for availability response."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AvailabilityWithUser(AvailabilityResponse):
    """Availability with user info for team view."""

    user_name: str
    user_email: str


# Availability Pattern schemas
class AvailabilityPatternBase(BaseModel):
    """Base schema for availability pattern."""

    pattern_type: PatternType = PatternType.WEEKLY
    day_of_week: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    start_date: date | None = None
    end_date: date | None = None
    note: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def validate_date_range(self) -> "AvailabilityPatternBase":
        """Validate that end_date is after start_date if both are provided."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after or equal to start_date")
        return self


class AvailabilityPatternCreate(AvailabilityPatternBase):
    """Schema for creating availability pattern."""

    pass


class AvailabilityPatternUpdate(BaseModel):
    """Schema for updating availability pattern."""

    pattern_type: PatternType | None = None
    day_of_week: int | None = Field(None, ge=0, le=6)
    status: AvailabilityStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
    note: str | None = Field(None, max_length=500)


class AvailabilityPatternResponse(AvailabilityPatternBase):
    """Schema for availability pattern response."""

    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Query schemas
class DateRangeQuery(BaseModel):
    """Schema for date range query parameters."""

    start_date: date
    end_date: date


# Bulk operations
class BulkAvailabilityCreate(BaseModel):
    """Schema for creating multiple availability entries."""

    entries: list[AvailabilityCreate]
