"""Parser for OnSong format files (.onsong).

OnSong is a popular iOS app for musicians. The format is text-based
with metadata headers and ChordPro-style chord notation.
"""

import re

from .base import BaseSongParser, ParseResult


class OnSongParser(BaseSongParser):
    """Parser for OnSong format.

    OnSong format characteristics:
    - Title is the first non-blank line
    - Artist can be second line (plain text, in parens, or after "by")
    - Metadata in "Key: Value" format (without curly braces)
    - Chords in square brackets: [G]Amazing [D7]grace
    - Section headers: "Verse:", "Chorus:", "Bridge:" on their own lines

    Common metadata:
    - Key: G
    - Tempo: 120
    - Capo: 2
    - Time: 4/4
    - CCLI: 12345
    - Copyright: ...
    """

    format_name = "onsong"

    # Regex patterns
    CHORD_PATTERN = re.compile(r"\[([A-Ga-g][#b♯♭]?[^\]]*)\]")
    METADATA_PATTERN = re.compile(r"^(Key|Tempo|Time|Capo|CCLI|Copyright|Duration|Flow):\s*(.+)$", re.IGNORECASE | re.MULTILINE)
    SECTION_PATTERN = re.compile(r"^(Verse|Chorus|Bridge|Pre-?Chorus|Tag|Intro|Outro|Interlude|Instrumental|Ending|Coda|Refrain|Hook|Vamp|Turnaround)(\s*\d*)\s*:?\s*$", re.IGNORECASE | re.MULTILINE)
    ARTIST_PREFIXES = re.compile(r"^(by|artist:?)\s+", re.IGNORECASE)

    def can_parse(self, content: str, filename: str) -> bool:
        """Check for OnSong format.

        Detection:
        1. File extension is .onsong
        2. Content has OnSong-style metadata AND section headers AND inline chords
           (to distinguish from Ultimate Guitar style with chords above lyrics)
        """
        # Check extension
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if ext == "onsong":
            return True

        # Check for OnSong characteristics in content:
        # - Has metadata lines without curly braces
        # - Has section headers
        # - Has inline ChordPro-style chords [G] (not chords on separate lines)
        # - Does NOT have ChordPro directives (to avoid confusion)
        has_chordpro_directives = bool(re.search(r"\{(title|artist|key|t|a):", content, re.IGNORECASE))
        if has_chordpro_directives:
            return False

        has_metadata = bool(self.METADATA_PATTERN.search(content))
        has_sections = bool(self.SECTION_PATTERN.search(content))
        has_inline_chords = bool(self.CHORD_PATTERN.search(content))

        # OnSong requires metadata + sections + inline chords
        # This distinguishes from Ultimate Guitar style (chords above lyrics)
        return has_metadata and has_sections and has_inline_chords

    def parse(self, content: str, filename: str) -> ParseResult:
        """Parse OnSong content."""
        try:
            lines = content.split("\n")
            title = None
            artist = None
            key = None
            tempo = None
            notes_parts: list[str] = []
            song_lines: list[str] = []
            metadata_ended = False
            line_idx = 0

            # Skip leading blank lines
            while line_idx < len(lines) and not lines[line_idx].strip():
                line_idx += 1

            # First non-blank line is the title
            if line_idx < len(lines):
                title = lines[line_idx].strip()
                line_idx += 1

            # Check next line for artist
            if line_idx < len(lines):
                next_line = lines[line_idx].strip()
                # Artist detection: in parens, after "by", or plain text before metadata
                if next_line.startswith("(") and next_line.endswith(")"):
                    artist = next_line[1:-1].strip()
                    line_idx += 1
                elif self.ARTIST_PREFIXES.match(next_line):
                    artist = self.ARTIST_PREFIXES.sub("", next_line).strip()
                    line_idx += 1
                elif not self.METADATA_PATTERN.match(next_line) and not self.SECTION_PATTERN.match(next_line) and not self.CHORD_PATTERN.search(next_line) and next_line:
                    # Plain text line that's not metadata, section, or lyrics with chords
                    artist = next_line
                    line_idx += 1

            # Process remaining lines
            for line in lines[line_idx:]:
                stripped = line.strip()

                # Check for metadata
                meta_match = self.METADATA_PATTERN.match(stripped)
                if meta_match and not metadata_ended:
                    meta_key, meta_value = meta_match.groups()
                    meta_key = meta_key.lower()
                    meta_value = meta_value.strip()

                    if meta_key == "key":
                        key = meta_value
                    elif meta_key == "tempo":
                        tempo_match = re.search(r"(\d+)", meta_value)
                        if tempo_match:
                            tempo_val = int(tempo_match.group(1))
                            if 20 <= tempo_val <= 300:
                                tempo = tempo_val
                    elif meta_key == "capo":
                        notes_parts.append(f"Capo: {meta_value}")
                    elif meta_key == "time":
                        notes_parts.append(f"Time: {meta_value}")
                    elif meta_key == "ccli":
                        notes_parts.append(f"CCLI: {meta_value}")
                    elif meta_key == "copyright":
                        notes_parts.append(f"Copyright: {meta_value}")
                    continue

                # Once we hit a section or lyrics with chords, metadata is done
                if self.SECTION_PATTERN.match(stripped) or self.CHORD_PATTERN.search(stripped) or (stripped and not meta_match):
                    metadata_ended = True

                # Add line to song content
                song_lines.append(line)

            # Use filename as title if not found
            if not title:
                title = self._extract_title_from_filename(filename)

            # Convert to ChordPro format
            chordpro_chart = self._convert_to_chordpro(title, artist, key, tempo, song_lines)

            # Extract plain lyrics
            lyrics = self._extract_lyrics(song_lines)

            # Normalize sections in lyrics
            normalized_lyrics, sections_normalized = self._normalize_sections(lyrics)

            # Extract chords and detect key
            chords = self._extract_chords("\n".join(song_lines))
            detected_key, key_confidence = self._detect_key_from_chords(chords)

            # Build notes
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
                    chordpro_chart=chordpro_chart,
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
                error=f"Failed to parse OnSong: {str(e)}",
                detected_format=self.format_name,
            )

    def _convert_to_chordpro(
        self,
        title: str | None,
        artist: str | None,
        key: str | None,
        tempo: int | None,
        song_lines: list[str],
    ) -> str:
        """Convert OnSong content to ChordPro format."""
        chordpro_lines: list[str] = []

        # Add metadata as ChordPro directives
        if title:
            chordpro_lines.append(f"{{title: {title}}}")
        if artist:
            chordpro_lines.append(f"{{artist: {artist}}}")
        if key:
            chordpro_lines.append(f"{{key: {key}}}")
        if tempo:
            chordpro_lines.append(f"{{tempo: {tempo}}}")

        if chordpro_lines:
            chordpro_lines.append("")  # Blank line after metadata

        # Process song lines
        for line in song_lines:
            stripped = line.strip()

            # Convert section headers to ChordPro comments
            section_match = self.SECTION_PATTERN.match(stripped)
            if section_match:
                section_name = section_match.group(1).title()
                section_num = section_match.group(2).strip() if section_match.group(2) else ""
                chordpro_lines.append(f"{{comment: {section_name}{section_num}}}")
            else:
                # Keep line as-is (chords in brackets are already ChordPro-compatible)
                chordpro_lines.append(stripped)

        return "\n".join(chordpro_lines)

    def _extract_lyrics(self, song_lines: list[str]) -> str:
        """Extract plain lyrics from OnSong content."""
        lyrics_lines: list[str] = []

        for line in song_lines:
            stripped = line.strip()

            # Skip metadata lines
            if self.METADATA_PATTERN.match(stripped):
                continue

            # Convert section headers to plain section names
            section_match = self.SECTION_PATTERN.match(stripped)
            if section_match:
                section_name = section_match.group(1).title()
                section_num = section_match.group(2).strip() if section_match.group(2) else ""
                lyrics_lines.append(f"[{section_name}{section_num}]")
                continue

            # Remove chords from line
            text = self.CHORD_PATTERN.sub("", stripped)
            lyrics_lines.append(text)

        # Clean up excessive blank lines
        result: list[str] = []
        prev_blank = False
        for line in lyrics_lines:
            is_blank = not line
            if is_blank and prev_blank:
                continue
            result.append(line)
            prev_blank = is_blank

        return "\n".join(result).strip()
