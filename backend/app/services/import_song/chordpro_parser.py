"""Parser for ChordPro format files (.cho, .crd, .chopro)."""

import re

from .base import BaseSongParser, ParseResult


class ChordProParser(BaseSongParser):
    """Parser for ChordPro format.

    ChordPro format uses:
    - Directives in curly braces: {title: Song Name}, {artist: Artist Name}
    - Chords in square brackets: [G]Amazing [D7]grace
    - Section markers: {start_of_verse}, {end_of_verse}

    Common directives:
    - {title:} or {t:} - Song title
    - {subtitle:} or {st:} - Subtitle (often artist)
    - {artist:} or {a:} - Artist name
    - {composer:} - Composer
    - {key:} - Musical key
    - {tempo:} - Tempo in BPM
    - {comment:} or {c:} - Comment/annotation
    """

    format_name = "chordpro"

    # Regex patterns
    DIRECTIVE_PATTERN = re.compile(r"\{(\w+):\s*(.+?)\}", re.IGNORECASE)
    CHORD_PATTERN = re.compile(r"\[([A-Ga-g][#b♯♭]?[^\]]*)\]")
    CHORDPRO_EXTENSIONS = {"cho", "crd", "chopro", "chordpro", "chord", "pro"}

    def can_parse(self, content: str, filename: str) -> bool:
        """Check for ChordPro format.

        Detection:
        1. File extension is .cho, .crd, .chopro, etc.
        2. Content contains ChordPro directives like {title:}
        """
        # Check extension
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if ext in self.CHORDPRO_EXTENSIONS:
            return True

        # Check for ChordPro directives in content
        return bool(self.DIRECTIVE_PATTERN.search(content))

    def parse(self, content: str, filename: str) -> ParseResult:
        """Parse ChordPro content."""
        try:
            title = None
            artist = None
            key = None
            tempo = None
            notes_parts: list[str] = []

            # Extract directives
            for match in self.DIRECTIVE_PATTERN.finditer(content):
                directive, value = match.groups()
                directive = directive.lower()
                value = value.strip()

                if directive in ("title", "t"):
                    if not title:  # Take first title
                        title = value
                elif directive in ("artist", "a"):
                    if not artist:
                        artist = value
                elif directive in ("subtitle", "st"):
                    # Subtitle often contains artist
                    if not artist:
                        artist = value
                elif directive == "composer":
                    notes_parts.append(f"Composer: {value}")
                elif directive == "key":
                    key = value
                elif directive == "tempo":
                    # Extract numeric BPM
                    tempo_match = re.search(r"(\d+)", value)
                    if tempo_match:
                        tempo_val = int(tempo_match.group(1))
                        if 20 <= tempo_val <= 300:
                            tempo = tempo_val
                elif directive == "capo":
                    notes_parts.append(f"Capo: {value}")
                elif directive == "duration":
                    notes_parts.append(f"Duration: {value}")
                elif directive in ("comment", "c"):
                    notes_parts.append(value)
                elif directive == "copyright":
                    notes_parts.append(f"Copyright: {value}")

            # Use filename as title if not found in content
            if not title:
                title = self._extract_title_from_filename(filename)

            # Extract plain lyrics (remove chords)
            lyrics = self._extract_lyrics(content)

            # Normalize sections in lyrics
            normalized_lyrics, sections_normalized = self._normalize_sections(lyrics)

            # Extract chords and detect key
            chords = self._extract_chords(content)
            detected_key, key_confidence = self._detect_key_from_chords(chords)

            # Build notes from collected parts
            notes = "\n".join(notes_parts) if notes_parts else None

            # Normalize specified key
            specified_key = self._normalize_key(key)

            # Use detected key if no specified key
            final_key = specified_key if specified_key else detected_key

            return ParseResult(
                success=True,
                song_data=self._build_song_data(
                    name=title,
                    artist=artist,
                    original_key=final_key,
                    tempo_bpm=tempo,
                    lyrics=normalized_lyrics,
                    chordpro_chart=content,  # Store original ChordPro
                    notes=notes,
                ),
                detected_format=self.format_name,
                specified_key=specified_key,
                detected_key=detected_key,
                key_confidence=key_confidence,
                sections_normalized=sections_normalized,
            )

        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Failed to parse ChordPro: {str(e)}",
                detected_format=self.format_name,
            )

    def _extract_lyrics(self, content: str) -> str:
        """Extract plain lyrics from ChordPro content.

        Removes:
        - Chord annotations [G], [Am7], etc.
        - Directives {title:}, {comment:}, etc.
        - Section markers {start_of_verse}, etc.
        """
        # Remove chords
        text = self.CHORD_PATTERN.sub("", content)

        # Remove directives
        text = re.sub(r"\{[^}]+\}", "", text)

        # Clean up whitespace
        lines = []
        for line in text.split("\n"):
            stripped = line.strip()
            lines.append(stripped)

        # Remove excessive blank lines
        result: list[str] = []
        prev_blank = False
        for line in lines:
            is_blank = not line
            if is_blank and prev_blank:
                continue
            result.append(line)
            prev_blank = is_blank

        return "\n".join(result).strip()
