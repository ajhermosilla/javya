"""Format detection and parsing orchestration for song imports."""

from .base import BaseSongParser, ParseResult
from .chordpro_parser import ChordProParser
from .openlyrics_parser import OpenLyricsParser
from .onsong_parser import OnSongParser
from .opensong_parser import OpenSongParser
from .plaintext_parser import PlainTextParser
from .ultimateguitar_parser import UltimateGuitarParser


# Parsers in order of detection priority
# More specific formats first, plain text as fallback
PARSERS: list[BaseSongParser] = [
    ChordProParser(),
    OpenLyricsParser(),
    OpenSongParser(),
    OnSongParser(),
    UltimateGuitarParser(),
    PlainTextParser(),  # Fallback - catches anything
]


def detect_and_parse(content: bytes, filename: str) -> ParseResult:
    """Detect file format and parse using appropriate parser.

    Args:
        content: Raw file content as bytes.
        filename: Original filename (used for format detection and title fallback).

    Returns:
        ParseResult with success status and parsed song data or error.
    """
    # Try multiple encodings in order of likelihood
    # - UTF-8: Modern standard
    # - Mac Roman: Legacy macOS encoding (used by OnSong iOS app exports)
    # - CP1252: Windows encoding
    # - Latin-1: Fallback (never fails, accepts any byte sequence)
    text_content = None
    for encoding in ("utf-8", "mac_roman", "cp1252", "latin-1"):
        try:
            text_content = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if text_content is None:
        return ParseResult(
            success=False,
            error="Could not decode file content",
            detected_format="unknown",
        )

    # Try each parser in order
    for parser in PARSERS:
        if parser.can_parse(text_content, filename):
            return parser.parse(text_content, filename)

    # Should never reach here since PlainTextParser always returns True
    return ParseResult(
        success=False,
        error="Could not detect file format",
        detected_format="unknown",
    )


def get_supported_formats() -> list[str]:
    """Get list of supported format names."""
    return [parser.format_name for parser in PARSERS]


def get_supported_extensions() -> list[str]:
    """Get list of supported file extensions."""
    return [
        ".cho",
        ".crd",
        ".chopro",
        ".chordpro",
        ".chord",
        ".pro",
        ".xml",
        ".txt",
        ".onsong",
    ]
