from enum import Enum


class UserRole(str, Enum):
    """User roles for authorization."""

    ADMIN = "admin"
    LEADER = "leader"
    MEMBER = "member"
