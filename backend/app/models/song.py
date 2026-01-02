import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Song(Base):
    """Song model for storing worship songs."""

    __tablename__ = "songs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    artist: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lyrics: Mapped[str | None] = mapped_column(Text, nullable=True)
    chordpro: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_key: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tempo: Mapped[int | None] = mapped_column(nullable=True)
    time_signature: Mapped[str | None] = mapped_column(String(10), nullable=True)
    mood: Mapped[str | None] = mapped_column(String(50), nullable=True)
    themes: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    ccli_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    youtube_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
