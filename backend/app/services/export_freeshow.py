"""FreeShow export service for generating presentation files."""

import re
import time
import uuid
from typing import Any

from app.models.setlist import Setlist


def generate_slide_id() -> str:
    """Generate a unique slide ID."""
    return str(uuid.uuid4())[:8]


def strip_chordpro(text: str) -> str:
    """Remove ChordPro chord annotations like [Am], [G], etc."""
    return re.sub(r"\[[A-Ga-g][#b]?[^]]*\]", "", text)


def parse_section_header(line: str) -> str | None:
    """Extract section name from header like [Verse 1] or [Chorus]."""
    match = re.match(r"^\[([^\]]+)\]$", line.strip())
    if match:
        header = match.group(1)
        # Check if it's a section header (not a chord)
        if not re.match(r"^[A-Ga-g][#b]?", header):
            return header
    return None


def parse_lyrics_to_slides(lyrics: str | None) -> list[dict[str, Any]]:
    """Parse lyrics text into FreeShow slide format.

    Splits by double newlines, detects section headers like [Verse 1].
    """
    if not lyrics:
        return []

    # Clean ChordPro annotations
    clean_lyrics = strip_chordpro(lyrics)

    # Split into sections by double newlines
    sections = re.split(r"\n\s*\n", clean_lyrics.strip())

    slides = []
    slide_counter = 1

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split("\n")
        group_name = None
        content_lines = []

        # Check if first line is a section header
        if lines:
            header = parse_section_header(lines[0])
            if header:
                group_name = header
                content_lines = lines[1:]
            else:
                content_lines = lines

        # Skip empty sections
        if not content_lines or not any(line.strip() for line in content_lines):
            continue

        # Default group name if not specified
        if not group_name:
            group_name = f"Slide {slide_counter}"

        slide_id = generate_slide_id()

        # Build text items for FreeShow
        text_lines = []
        for line in content_lines:
            if line.strip():
                text_lines.append({
                    "align": "",
                    "text": [{"value": line.strip(), "style": ""}]
                })

        slides.append({
            "id": slide_id,
            "group": group_name,
            "color": None,
            "settings": {},
            "notes": "",
            "items": [{
                "type": "text",
                "lines": text_lines,
                "style": "top: 120px; left: 50px; height: 840px; width: 1820px;",
                "align": ""
            }]
        })

        slide_counter += 1

    return slides


def generate_freeshow_show(song_name: str, artist: str | None, key: str | None,
                           lyrics: str | None, notes: str | None = None) -> dict[str, Any]:
    """Generate a FreeShow .show structure for a single song."""
    now = int(time.time())

    slides = parse_lyrics_to_slides(lyrics)

    # Build slides dict
    slides_dict = {}
    layout_slides = []

    for slide in slides:
        slide_id = slide["id"]
        slides_dict[slide_id] = {
            "group": slide["group"],
            "color": slide["color"],
            "settings": slide["settings"],
            "notes": slide["notes"],
            "items": slide["items"]
        }
        layout_slides.append({"id": slide_id})

    return {
        "name": song_name,
        "category": None,
        "settings": {
            "activeLayout": "default"
        },
        "timestamps": {
            "created": now,
            "modified": now,
            "used": now
        },
        "meta": {
            "title": song_name,
            "artist": artist or "",
            "key": key or ""
        },
        "slides": slides_dict,
        "layouts": {
            "default": {
                "slides": layout_slides
            }
        },
        "media": {}
    }


def generate_freeshow_project(setlist: Setlist) -> dict[str, Any]:
    """Generate a FreeShow .project structure for a setlist.

    Creates a project containing all songs in the setlist.
    """
    now = int(time.time())

    project_shows = []
    shows_dict = {}

    for setlist_song in setlist.songs:
        song = setlist_song.song
        show_id = str(uuid.uuid4())[:8]

        # Add to project shows list
        project_shows.append({"id": show_id})

        # Generate the show content
        shows_dict[show_id] = generate_freeshow_show(
            song_name=song.name,
            artist=song.artist,
            key=song.preferred_key or song.original_key,
            lyrics=song.lyrics,
            notes=setlist_song.notes
        )

    return {
        "project": {
            "name": setlist.name,
            "created": now,
            "modified": now,
            "parent": "/",
            "shows": project_shows
        },
        "shows": shows_dict
    }
