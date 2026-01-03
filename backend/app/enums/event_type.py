from enum import Enum


class EventType(str, Enum):
    SUNDAY = "Sunday"
    WEDNESDAY = "Wednesday"
    YOUTH = "Youth"
    SPECIAL = "Special"
    RETREAT = "Retreat"
    OTHER = "Other"
