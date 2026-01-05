from app.schemas.song import SongCreate, SongResponse, SongUpdate
from app.schemas.setlist import (
    SetlistCreate,
    SetlistUpdate,
    SetlistResponse,
    SetlistDetailResponse,
    SetlistSongCreate,
    SetlistSongResponse,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserRoleUpdate,
    UserResponse,
    Token,
    TokenData,
)
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
    AvailabilityWithUser,
    AvailabilityPatternCreate,
    AvailabilityPatternUpdate,
    AvailabilityPatternResponse,
    DateRangeQuery,
    BulkAvailabilityCreate,
)

__all__ = [
    # Song
    "SongCreate",
    "SongUpdate",
    "SongResponse",
    # Setlist
    "SetlistCreate",
    "SetlistUpdate",
    "SetlistResponse",
    "SetlistDetailResponse",
    "SetlistSongCreate",
    "SetlistSongResponse",
    # User
    "UserCreate",
    "UserUpdate",
    "UserRoleUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    # Availability
    "AvailabilityCreate",
    "AvailabilityUpdate",
    "AvailabilityResponse",
    "AvailabilityWithUser",
    "AvailabilityPatternCreate",
    "AvailabilityPatternUpdate",
    "AvailabilityPatternResponse",
    "DateRangeQuery",
    "BulkAvailabilityCreate",
]
