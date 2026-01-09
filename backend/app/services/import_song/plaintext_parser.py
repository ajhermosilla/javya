"""Parser for plain text song files (.txt, unstructured)."""

import re

from .base import BaseSongParser, ParseResult


class PlainTextParser(BaseSongParser):
    """Heuristic parser for plain text files.

    This parser handles unstructured text files with various formats:
    - Chord-over-lyrics (Ultimate Guitar style)
    - Metadata at top of file (Title:, Artist:, Key:)
    - Section markers in brackets [Verse 1], [Chorus]

    This is the fallback parser - it always returns True for can_parse()
    and attempts to extract whatever it can from the content.
    """

    format_name = "plaintext"

    # Metadata patterns
    TITLE_PATTERNS = [
        re.compile(r"^title:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^song:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^name:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    ]
    ARTIST_PATTERNS = [
        re.compile(r"^artist:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^by:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^author:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^performer:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    ]
    KEY_PATTERNS = [
        re.compile(r"^key:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^key\s+of\s+(.+)$", re.IGNORECASE | re.MULTILINE),
    ]
    TEMPO_PATTERNS = [
        re.compile(r"^tempo:\s*(\d+)", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^bpm:\s*(\d+)", re.IGNORECASE | re.MULTILINE),
    ]

    # Chord detection pattern
    CHORD_PATTERN = re.compile(
        r"^[\s]*"
        r"([A-G][#b♯♭]?"
        r"(?:maj|min|m|dim|aug|sus[24]?|add[29]?|7|9|11|13|6)?"
        r"(?:/[A-G][#b♯♭]?)?"
        r"[\s]+)*"
        r"[A-G][#b♯♭]?"
        r"(?:maj|min|m|dim|aug|sus[24]?|add[29]?|7|9|11|13|6)?"
        r"(?:/[A-G][#b♯♭]?)?"
        r"[\s]*$"
    )

    # Individual chord pattern for extraction
    SINGLE_CHORD_PATTERN = re.compile(
        r"([A-G][#b♯♭]?"
        r"(?:maj|min|m|dim|aug|sus[24]?|add[29]?|7|9|11|13|6)?"
        r"(?:/[A-G][#b♯♭]?)?)"
    )

    def can_parse(self, content: str, filename: str) -> bool:
        """Plain text is the fallback - always returns True."""
        return True

    def parse(self, content: str, filename: str) -> ParseResult:
        """Parse plain text content using heuristics."""
        try:
            # Extract metadata
            title = self._extract_pattern(content, self.TITLE_PATTERNS)
            artist = self._extract_pattern(content, self.ARTIST_PATTERNS)
            key = self._extract_pattern(content, self.KEY_PATTERNS)
            tempo_str = self._extract_pattern(content, self.TEMPO_PATTERNS)

            tempo = None
            if tempo_str:
                try:
                    tempo_val = int(tempo_str)
                    if 20 <= tempo_val <= 300:
                        tempo = tempo_val
                except ValueError:
                    pass

            # Clean content - remove metadata lines
            cleaned = self._remove_metadata_lines(content)

            # Try to infer title from first non-empty line if not found
            if not title:
                title = self._infer_title(cleaned, filename)

            # Detect and convert chord-over-lyrics format
            has_chords, chordpro = self._detect_and_convert_chords(cleaned)

            # Extract plain lyrics
            lyrics = self._extract_plain_lyrics(cleaned)

            # Normalize sections in lyrics
            normalized_lyrics, sections_normalized = self._normalize_sections(lyrics)

            # Extract chords and detect key from ChordPro content
            chords = self._extract_chords(chordpro) if has_chords else []
            detected_key, key_confidence = self._detect_key_from_chords(chords)

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
                    chordpro_chart=chordpro if has_chords else None,
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
                error=f"Failed to parse plain text: {str(e)}",
                detected_format=self.format_name,
            )

    def _extract_pattern(
        self, content: str, patterns: list[re.Pattern[str]]
    ) -> str | None:
        """Extract first match from a list of patterns."""
        for pattern in patterns:
            match = pattern.search(content)
            if match:
                return match.group(1).strip()
        return None

    def _remove_metadata_lines(self, content: str) -> str:
        """Remove metadata lines from content."""
        result = content

        all_patterns = (
            self.TITLE_PATTERNS
            + self.ARTIST_PATTERNS
            + self.KEY_PATTERNS
            + self.TEMPO_PATTERNS
        )

        for pattern in all_patterns:
            result = pattern.sub("", result)

        return result

    def _infer_title(self, content: str, filename: str) -> str:
        """Infer title from content or filename.

        Strategy:
        1. First non-empty, non-chord line that looks like a title
        2. Fall back to filename
        """
        lines = content.split("\n")

        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if not line:
                continue

            # Skip if it looks like a chord line
            if self._is_chord_line(line):
                continue

            # Skip if it looks like a section marker
            if line.startswith("[") and line.endswith("]"):
                continue

            # Use this line as title if it's not too long
            if len(line) <= 100:
                return line

        # Fall back to filename
        return self._extract_title_from_filename(filename)

    def _is_chord_line(self, line: str) -> bool:
        """Check if a line contains only chords."""
        if not line.strip():
            return False

        # Must match chord pattern
        if not self.CHORD_PATTERN.match(line):
            return False

        # Should have at least one chord
        return bool(self.SINGLE_CHORD_PATTERN.search(line))

    def _detect_and_convert_chords(self, content: str) -> tuple[bool, str]:
        """Detect chord-over-lyrics pattern and convert to ChordPro.

        Returns:
            Tuple of (has_chords, chordpro_content)
        """
        lines = content.split("\n")
        result_lines: list[str] = []
        has_chords = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a chord line followed by a lyric line
            if self._is_chord_line(line) and i + 1 < len(lines):
                next_line = lines[i + 1]

                # Next line should be lyrics (not another chord line, not empty)
                if not self._is_chord_line(next_line) and next_line.strip():
                    has_chords = True
                    merged = self._merge_chord_with_lyric(line, next_line)
                    result_lines.append(merged)
                    i += 2
                    continue

            result_lines.append(line)
            i += 1

        return has_chords, "\n".join(result_lines)

    def _merge_chord_with_lyric(self, chord_line: str, lyric_line: str) -> str:
        """Merge a chord line with a lyric line into ChordPro format."""
        # Find chord positions
        chords: list[tuple[int, str]] = []

        for match in self.SINGLE_CHORD_PATTERN.finditer(chord_line):
            chords.append((match.start(), match.group(0)))

        if not chords:
            return lyric_line.rstrip()

        # Insert chords at positions
        result = lyric_line.rstrip()
        offset = 0

        for pos, chord in sorted(chords):
            insert_pos = min(pos + offset, len(result))
            chord_markup = f"[{chord}]"
            result = result[:insert_pos] + chord_markup + result[insert_pos:]
            offset += len(chord_markup)

        return result

    def _extract_plain_lyrics(self, content: str) -> str:
        """Extract plain lyrics, removing chord lines."""
        lines = content.split("\n")
        result_lines: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip chord lines that are followed by lyric lines
            if self._is_chord_line(line):
                if i + 1 < len(lines) and not self._is_chord_line(lines[i + 1]):
                    # This chord line will be merged with next line, skip it
                    i += 1
                    continue
                else:
                    # Standalone chord line (instrumental), skip it
                    i += 1
                    continue

            result_lines.append(line.rstrip())
            i += 1

        # Clean up excessive blank lines
        cleaned: list[str] = []
        prev_blank = False
        for line in result_lines:
            is_blank = not line.strip()
            if is_blank and prev_blank:
                continue
            cleaned.append(line)
            prev_blank = is_blank

        return "\n".join(cleaned).strip()
