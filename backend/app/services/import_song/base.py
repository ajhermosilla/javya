"""Base classes for song file parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.enums import MusicalKey
from app.schemas.song import SongCreate


@dataclass
class ParseResult:
    """Result from parsing a song file."""

    success: bool
    song_data: SongCreate | None = None
    error: str | None = None
    detected_format: str = "unknown"


class BaseSongParser(ABC):
    """Abstract base class for song format parsers."""

    format_name: str = "unknown"

    @abstractmethod
    def can_parse(self, content: str, filename: str) -> bool:
        """Check if this parser can handle the content.

        Args:
            content: The file content as a string.
            filename: The original filename.

        Returns:
            True if this parser can handle the content.
        """
        pass

    @abstractmethod
    def parse(self, content: str, filename: str) -> ParseResult:
        """Parse the content and return a ParseResult.

        Args:
            content: The file content as a string.
            filename: The original filename.

        Returns:
            ParseResult with success status and parsed song data or error.
        """
        pass

    def _normalize_key(self, key_str: str | None) -> MusicalKey | None:
        """Normalize a key string to MusicalKey enum.

        Handles common variations like "G major", "Gm", "G#", etc.

        Args:
            key_str: The key string to normalize.

        Returns:
            MusicalKey enum value or None if not recognized.
        """
        if not key_str:
            return None

        # Clean up the key string
        key = key_str.strip()

        # Remove common suffixes
        for suffix in ["major", "maj", "minor", "min", "m"]:
            if key.lower().endswith(suffix):
                key = key[: -len(suffix)].strip()
                break

        # Normalize common variations
        key_map: dict[str, MusicalKey] = {
            # Natural
            "C": MusicalKey.C,
            # Sharp keys
            "G": MusicalKey.G,
            "D": MusicalKey.D,
            "A": MusicalKey.A,
            "E": MusicalKey.E,
            "B": MusicalKey.B,
            "F#": MusicalKey.F_SHARP,
            "F♯": MusicalKey.F_SHARP,
            "Gb": MusicalKey.G_FLAT,
            "G♭": MusicalKey.G_FLAT,
            "C#": MusicalKey.C_SHARP,
            "C♯": MusicalKey.C_SHARP,
            "Db": MusicalKey.D_FLAT,
            "D♭": MusicalKey.D_FLAT,
            # Flat keys
            "F": MusicalKey.F,
            "Bb": MusicalKey.B_FLAT,
            "B♭": MusicalKey.B_FLAT,
            "Eb": MusicalKey.E_FLAT,
            "E♭": MusicalKey.E_FLAT,
            "Ab": MusicalKey.A_FLAT,
            "A♭": MusicalKey.A_FLAT,
            # Enharmonic equivalents
            "D#": MusicalKey.D_SHARP,
            "D♯": MusicalKey.D_SHARP,
            "G#": MusicalKey.G_SHARP,
            "G♯": MusicalKey.G_SHARP,
            "A#": MusicalKey.A_SHARP,
            "A♯": MusicalKey.A_SHARP,
        }

        return key_map.get(key)

    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract a title from the filename.

        Args:
            filename: The original filename.

        Returns:
            Title extracted from filename (without extension).
        """
        # Remove extension
        name = filename.rsplit(".", 1)[0] if "." in filename else filename

        # Replace underscores and hyphens with spaces
        name = name.replace("_", " ").replace("-", " ")

        # Title case and clean up extra spaces
        return " ".join(name.split()).title()

    def _build_song_data(self, **kwargs: Any) -> SongCreate:
        """Build a SongCreate object from parsed data.

        Args:
            **kwargs: Parsed song fields.

        Returns:
            SongCreate object.
        """
        # Filter out None values and empty strings
        filtered = {
            k: v for k, v in kwargs.items() if v is not None and v != ""
        }

        return SongCreate(**filtered)
