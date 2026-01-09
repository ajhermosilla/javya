"""Base classes for song file parsers."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.enums import MusicalKey
from app.schemas.song import SongCreate
from .key_detector import KeyDetector
from .section_detector import SectionDetector


@dataclass
class ParseResult:
    """Result from parsing a song file."""

    success: bool
    song_data: SongCreate | None = None
    error: str | None = None
    detected_format: str = "unknown"

    # Key detection results
    specified_key: MusicalKey | None = None  # From file metadata
    detected_key: MusicalKey | None = None  # From chord analysis
    key_confidence: str | None = None  # "high", "medium", "low"

    # Section detection results
    sections_normalized: bool = False  # Whether markers were normalized


class BaseSongParser(ABC):
    """Abstract base class for song format parsers."""

    format_name: str = "unknown"

    # Shared detectors for all parsers
    _key_detector = KeyDetector()
    _section_detector = SectionDetector()

    # Chord pattern for extraction - matches [G], [Am7], etc.
    CHORD_PATTERN = re.compile(r"\[([A-Ga-g][#b♯♭]?[^\]]*)\]")

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

    def _extract_chords(self, content: str) -> list[str]:
        """Extract chord names from content.

        Args:
            content: Content with chords in [brackets].

        Returns:
            List of chord strings.
        """
        return self.CHORD_PATTERN.findall(content)

    def _detect_key_from_chords(
        self, chords: list[str]
    ) -> tuple[MusicalKey | None, str | None]:
        """Detect key from a list of chords.

        Args:
            chords: List of chord strings.

        Returns:
            Tuple of (detected_key, confidence_level)
        """
        if not chords:
            return None, None

        result = self._key_detector.detect_key(chords)
        return result.detected_key, result.confidence.value if result.detected_key else None

    def _normalize_sections(self, lyrics: str) -> tuple[str, bool]:
        """Normalize section markers in lyrics.

        Args:
            lyrics: Lyrics text.

        Returns:
            Tuple of (normalized_lyrics, had_markers_normalized)
        """
        if not lyrics or not lyrics.strip():
            return lyrics, False

        result = self._section_detector.detect_sections(lyrics)
        # Only return normalized content if markers were found or sections were detected
        if result.had_existing_markers or result.sections:
            return result.normalized_content, result.had_existing_markers
        return lyrics, False
