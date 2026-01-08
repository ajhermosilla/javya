"""Song import service - parses various song file formats.

Supported formats:
- ChordPro (.cho, .crd, .chopro)
- OpenLyrics/OpenLP (.xml)
- OpenSong (.xml)
- Plain Text (.txt)

Usage:
    from app.services.import_song import detect_and_parse

    result = detect_and_parse(file_content, filename)
    if result.success:
        song_data = result.song_data
    else:
        error_message = result.error
"""

from .base import ParseResult
from .detector import detect_and_parse, get_supported_extensions, get_supported_formats

__all__ = [
    "detect_and_parse",
    "get_supported_formats",
    "get_supported_extensions",
    "ParseResult",
]
