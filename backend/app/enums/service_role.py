from enum import Enum


class ServiceRole(str, Enum):
    """Roles that team members can fulfill in a service."""

    WORSHIP_LEADER = "worship_leader"
    VOCALIST = "vocalist"
    GUITARIST = "guitarist"
    BASSIST = "bassist"
    DRUMMER = "drummer"
    KEYS = "keys"
    SOUND = "sound"
    PROJECTION = "projection"
    OTHER = "other"
