"""Quelea export service for generating .qsch schedule files."""

import io
import re
import zipfile
from xml.etree import ElementTree as ET
from xml.dom import minidom

from app.models.setlist import Setlist


def escape_xml(text: str | None) -> str:
    """Escape special XML characters."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def strip_chordpro(text: str) -> str:
    """Remove ChordPro chord annotations like [Am], [G], etc."""
    return re.sub(r"\[[A-Ga-g][#b]?[^]]*\]", "", text)


def parse_lyrics_to_sections(lyrics: str | None) -> list[str]:
    """Parse lyrics into sections (split by double newlines)."""
    if not lyrics:
        return []

    clean_lyrics = strip_chordpro(lyrics)
    sections = re.split(r"\n\s*\n", clean_lyrics.strip())

    result = []
    for section in sections:
        lines = []
        for line in section.strip().split("\n"):
            # Skip section headers like [Verse 1]
            if line.strip() and not re.match(r"^\[.+\]$", line.strip()):
                lines.append(line.strip())
        if lines:
            result.append("\n".join(lines))

    return result


def generate_song_xml(song, notes: str | None = None) -> str:
    """Generate Quelea XML for a single song."""
    # Build lyrics sections
    sections = parse_lyrics_to_sections(song.lyrics)
    lyrics_parts = []
    for section in sections:
        lyrics_parts.append(f"  <section>{escape_xml(section)}</section>")

    lyrics_xml = "\n".join(lyrics_parts) if lyrics_parts else ""

    key = song.preferred_key or song.original_key or ""

    return f"""<song>
  <title>{escape_xml(song.name)}</title>
  <author>{escape_xml(song.artist or "")}</author>
  <key>{escape_xml(key)}</key>
  <ccli></ccli>
  <copyright></copyright>
  <year></year>
  <publisher></publisher>
  <notes>{escape_xml(notes or song.notes or "")}</notes>
  <lyrics>
{lyrics_xml}
  </lyrics>
</song>"""


def generate_quelea_schedule(setlist: Setlist) -> bytes:
    """Generate a Quelea .qsch schedule file (ZIP containing schedule.xml).

    Returns the ZIP file as bytes.
    """
    # Build schedule XML
    songs_xml = []
    for setlist_song in setlist.songs:
        song_xml = generate_song_xml(setlist_song.song, setlist_song.notes)
        songs_xml.append(song_xml)

    schedule_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<schedule>
{"".join(songs_xml)}
</schedule>"""

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("schedule.xml", schedule_xml.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
