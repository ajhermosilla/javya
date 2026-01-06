"""PDF export service for generating musician chord charts and setlist summaries."""

import re
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

from app.models.setlist import Setlist


def is_section_header(line: str) -> bool:
    """Check if line is a section header like [Verse 1], not a chord.

    Section headers are bracketed text that is NOT a chord.
    Chords are single notes (A-G) optionally with sharps/flats and qualities.
    """
    match = re.match(r"^\[([^\]]+)\]$", line)
    if not match:
        return False

    content = match.group(1)

    # Check if this looks like a chord (matches chord pattern)
    # Chords: A, Am, G7, Cmaj7, F#m, Bb, Dsus4, etc.
    # Pattern: Root note (A-G) + optional accidental (#/b) + optional quality
    chord_pattern = r"^[A-Ga-g][#b]?(m|maj|min|dim|aug|sus|add|[0-9])*[0-9]*$"
    if re.match(chord_pattern, content):
        return False

    # If it doesn't look like a chord, it's a section header
    return True


def extract_section_name(line: str) -> str:
    """Extract section name from header like [Verse 1]."""
    match = re.match(r"^\[([^\]]+)\]$", line)
    return match.group(1) if match else line


def parse_directive(line: str) -> str | None:
    """Parse ChordPro directive like {comment: Play softly}."""
    match = re.match(r"\{(\w+):\s*(.+)\}", line)
    if match:
        directive_type = match.group(1).lower()
        value = match.group(2)
        if directive_type in ("comment", "c"):
            return f'<div class="comment">{value}</div>'
        elif directive_type == "title":
            return f'<div class="directive-title">{value}</div>'
    return None


def render_chord_line(line: str) -> str:
    """Render a line with chords as HTML with chord spans above lyrics.

    Input: [G]Amazing [G7]grace
    Output: HTML with styled chord spans
    """
    # Split by chord annotations, keeping the chords
    parts = re.split(r"(\[[^\]]+\])", line)

    html_parts = []
    for i, part in enumerate(parts):
        if part.startswith("[") and part.endswith("]"):
            chord = part[1:-1]
            html_parts.append(f'<span class="chord">{chord}</span>')
        elif part:
            # Escape HTML entities
            escaped = part.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_parts.append(f'<span class="lyric">{escaped}</span>')

    return f'<div class="chord-line">{"".join(html_parts)}</div>'


def parse_chordpro_to_html(chordpro: str | None) -> str:
    """Convert ChordPro notation to HTML with inline chords.

    Handles:
    - Chord annotations [Am], [G7], [Cmaj7], etc.
    - Section headers [Verse 1], [Chorus], etc.
    - ChordPro directives {comment:...}, {title:...}
    - Preserves line breaks and spacing
    """
    if not chordpro:
        return ""

    lines = chordpro.split("\n")
    html_lines = []

    for line in lines:
        stripped = line.strip()

        # Check for section header (e.g., [Verse 1], [Chorus])
        if is_section_header(stripped):
            section_name = extract_section_name(stripped)
            html_lines.append(f'<div class="section-header">{section_name}</div>')
            continue

        # Check for ChordPro directives like {title:...}
        if stripped.startswith("{") and stripped.endswith("}"):
            directive = parse_directive(stripped)
            if directive:
                html_lines.append(directive)
            continue

        # Process chord line
        if "[" in stripped and "]" in stripped:
            html_lines.append(render_chord_line(stripped))
        elif stripped:
            # Plain lyric line without chords
            escaped = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_lines.append(f'<div class="lyric-line">{escaped}</div>')
        else:
            # Empty line
            html_lines.append('<div class="empty-line"></div>')

    return "\n".join(html_lines)


def strip_chordpro_for_summary(text: str | None) -> str:
    """Remove ChordPro annotations for summary view."""
    if not text:
        return ""
    return re.sub(r"\[[^\]]+\]", "", text)


def get_pdf_styles() -> str:
    """Return CSS styles for PDF generation."""
    return """
    @page {
        size: letter;
        margin: 0.75in;
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10pt;
            color: #666;
        }
    }

    body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #333;
    }

    /* Header styles */
    .setlist-header {
        text-align: center;
        margin-bottom: 1.5em;
        padding-bottom: 1em;
        border-bottom: 2px solid #333;
    }

    .setlist-header.title-page {
        page-break-after: always;
        border-bottom: none;
        padding-top: 2in;
    }

    .setlist-title {
        font-size: 24pt;
        font-weight: bold;
        margin: 0 0 0.25em 0;
    }

    .setlist-meta {
        font-size: 12pt;
        color: #666;
    }

    .setlist-description {
        margin-top: 0.5em;
        font-style: italic;
    }

    .song-list {
        margin-top: 2em;
        text-align: left;
        display: inline-block;
    }

    .song-list-item {
        margin: 0.25em 0;
        font-size: 11pt;
    }

    /* Song table for summary */
    .song-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1em;
    }

    .song-table th {
        text-align: left;
        padding: 0.5em;
        border-bottom: 2px solid #333;
        font-weight: bold;
        background-color: #f5f5f5;
    }

    .song-table td {
        padding: 0.5em;
        border-bottom: 1px solid #ddd;
        vertical-align: top;
    }

    .song-table .song-number {
        width: 2em;
        text-align: center;
        font-weight: bold;
    }

    .song-table .song-name {
        font-weight: 500;
    }

    .song-table .song-key {
        width: 3em;
        text-align: center;
    }

    .song-table .song-tempo {
        width: 3em;
        text-align: center;
    }

    /* Chord chart styles */
    .song-page {
        page-break-after: always;
    }

    .song-page:last-child {
        page-break-after: auto;
    }

    .song-header {
        margin-bottom: 1em;
        padding-bottom: 0.5em;
        border-bottom: 1px solid #ccc;
    }

    .song-title {
        font-size: 16pt;
        font-weight: bold;
        margin: 0 0 0.25em 0;
    }

    .song-meta {
        font-size: 10pt;
        color: #666;
    }

    .chord-chart {
        font-family: 'Courier New', Courier, monospace;
        font-size: 10pt;
        line-height: 2.2;
    }

    .section-header {
        font-weight: bold;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        color: #333;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 11pt;
    }

    .chord-line {
        position: relative;
        white-space: pre-wrap;
    }

    .chord {
        color: #0066cc;
        font-weight: bold;
        font-size: 9pt;
        vertical-align: super;
        margin-right: 0.1em;
    }

    .lyric {
        display: inline;
    }

    .lyric-line {
        margin-bottom: 0.25em;
    }

    .empty-line {
        height: 1em;
    }

    .comment {
        font-style: italic;
        color: #666;
        margin: 0.5em 0;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }

    .directive-title {
        font-weight: bold;
        margin: 0.5em 0;
    }

    .song-notes {
        margin-top: 1em;
        padding: 0.5em 0.75em;
        background-color: #fffde7;
        border-left: 3px solid #ffc107;
        font-size: 9pt;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }

    .footer-note {
        margin-top: 2em;
        text-align: center;
        font-size: 9pt;
        color: #999;
    }
    """


def _get_template_env() -> Environment:
    """Get Jinja2 environment with templates directory."""
    templates_dir = Path(__file__).parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html"]),
    )


def generate_pdf_summary(setlist: Setlist) -> bytes:
    """Generate a summary PDF with song overview.

    Includes: song titles, keys, tempo, artist, notes
    """
    env = _get_template_env()
    template = env.get_template("pdf_summary.html")

    songs_data = []
    for setlist_song in setlist.songs:
        song = setlist_song.song
        songs_data.append(
            {
                "position": setlist_song.position + 1,
                "name": song.name,
                "artist": song.artist or "",
                "key": song.preferred_key or song.original_key or "",
                "tempo": song.tempo_bpm,
                "notes": setlist_song.notes or song.notes or "",
            }
        )

    html_content = template.render(
        setlist_name=setlist.name,
        service_date=setlist.service_date,
        event_type=setlist.event_type,
        description=setlist.description,
        songs=songs_data,
        generated_date=date.today(),
    )

    css = CSS(string=get_pdf_styles())
    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[css])

    return pdf_bytes


def generate_pdf_chord_charts(setlist: Setlist) -> bytes:
    """Generate a full chord charts PDF with ChordPro lyrics.

    Includes: full song lyrics with inline chords for each song
    """
    env = _get_template_env()
    template = env.get_template("pdf_chord_charts.html")

    songs_data = []
    for setlist_song in setlist.songs:
        song = setlist_song.song
        # Prefer chordpro_chart if available, fall back to lyrics
        chart_source = song.chordpro_chart or song.lyrics
        chord_html = parse_chordpro_to_html(chart_source)

        songs_data.append(
            {
                "position": setlist_song.position + 1,
                "name": song.name,
                "artist": song.artist or "",
                "key": song.preferred_key or song.original_key or "",
                "tempo": song.tempo_bpm,
                "chord_chart_html": chord_html,
                "notes": setlist_song.notes or "",
            }
        )

    html_content = template.render(
        setlist_name=setlist.name,
        service_date=setlist.service_date,
        event_type=setlist.event_type,
        songs=songs_data,
        generated_date=date.today(),
    )

    css = CSS(string=get_pdf_styles())
    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[css])

    return pdf_bytes
