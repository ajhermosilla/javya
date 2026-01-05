from enum import Enum


class AvailabilityStatus(str, Enum):
    """Availability status for a specific date."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAYBE = "maybe"


class PatternType(str, Enum):
    """Recurrence pattern types for availability."""

    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
