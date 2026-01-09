"""Parser for Ultimate Guitar format files."""

import re

from .base import BaseSongParser, ParseResult


class UltimateGuitarParser(BaseSongParser):
    """Parser for Ultimate Guitar chord/tab format.

    Ultimate Guitar format characteristics:
    - Chord-over-lyrics style (chords on line above lyrics)
    - Section markers in brackets: [Verse], [Chorus], [Bridge], [Intro], [Outro]
    - Common metadata: Capo, Tuning, Key, Difficulty
    - May contain [tab] or [/tab] markers for tablature sections
    - Often has "ultimate-guitar" or "UG" references
    """

    format_name = "ultimateguitar"

    # Detection patterns
    CAPO_PATTERN = re.compile(r"^capo[:\s]+(\d+)", re.IGNORECASE | re.MULTILINE)
    TUNING_PATTERN = re.compile(
        r"^tuning[:\s]+([A-Ga-g#b\s]+)", re.IGNORECASE | re.MULTILINE
    )
    KEY_PATTERN = re.compile(r"^key[:\s]+([A-G][#b]?m?)", re.IGNORECASE | re.MULTILINE)

    # UG-specific section markers (more specific than generic plaintext)
    SECTION_PATTERN = re.compile(
        r"^\[?(Verse|Chorus|Bridge|Intro|Outro|Pre-Chorus|Interlude|Solo|Hook|Refrain)"
        r"(?:\s*\d+)?\]?$",
        re.IGNORECASE | re.MULTILINE,
    )

    # Title/Artist patterns - UG often has these at the top
    TITLE_PATTERNS = [
        re.compile(r"^(.+)\s+(?:by|[-–—])\s+(.+)$", re.MULTILINE),  # "Title by Artist" or "Title - Artist"
        re.compile(r"^title[:\s]+(.+)$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^song[:\s]+(.+)$", re.IGNORECASE | re.MULTILINE),
    ]
    ARTIST_PATTERN = re.compile(r"^artist[:\s]+(.+)$", re.IGNORECASE | re.MULTILINE)

    # Chord detection (same as plaintext but reused here)
    CHORD_LINE_PATTERN = re.compile(
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

    SINGLE_CHORD_PATTERN = re.compile(
        r"([A-G][#b♯♭]?"
        r"(?:maj|min|m|dim|aug|sus[24]?|add[29]?|7|9|11|13|6)?"
        r"(?:/[A-G][#b♯♭]?)?)"
    )

    def can_parse(self, content: str, filename: str) -> bool:
        """Detect Ultimate Guitar format.

        Detection criteria (any of):
        - Has Capo: line
        - Has Tuning: line
        - Has multiple UG-style section markers
        - Has [tab] or [/tab] markers
        - Filename contains 'ug' or 'ultimate'
        """
        content_lower = content.lower()

        # Check filename hints
        filename_lower = filename.lower()
        if "ultimate" in filename_lower or "_ug" in filename_lower or "-ug" in filename_lower:
            return True

        # Check for Capo line (very common in UG)
        if self.CAPO_PATTERN.search(content):
            return True

        # Check for Tuning line
        if self.TUNING_PATTERN.search(content):
            return True

        # Check for tab markers
        if "[tab]" in content_lower or "[/tab]" in content_lower:
            return True

        # Check for multiple section markers (at least 2)
        sections = self.SECTION_PATTERN.findall(content)
        if len(sections) >= 2:
            # Also verify there are chord lines (to distinguish from plain lyrics)
            lines = content.split("\n")
            chord_lines = sum(1 for line in lines if self._is_chord_line(line))
            if chord_lines >= 2:
                return True

        return False

    def parse(self, content: str, filename: str) -> ParseResult:
        """Parse Ultimate Guitar format content."""
        try:
            # Extract metadata
            title, artist = self._extract_title_artist(content, filename)
            capo = self._extract_capo(content)
            tuning = self._extract_tuning(content)
            key = self._extract_key(content)

            # Clean content - remove metadata lines
            cleaned = self._remove_metadata_lines(content)

            # Convert chord-over-lyrics to ChordPro
            chordpro = self._convert_to_chordpro(cleaned)

            # Extract plain lyrics
            lyrics = self._extract_plain_lyrics(cleaned)

            # Normalize sections in lyrics
            normalized_lyrics, sections_normalized = self._normalize_sections(lyrics)

            # Extract chords and detect key from ChordPro content
            chords = self._extract_chords(chordpro)
            detected_key, key_confidence = self._detect_key_from_chords(chords)

            # Build notes from capo and tuning info
            notes_parts = []
            if capo:
                notes_parts.append(f"Capo: {capo}")
            if tuning:
                notes_parts.append(f"Tuning: {tuning}")
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
                    lyrics=normalized_lyrics,
                    chordpro_chart=chordpro,
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
                error=f"Failed to parse Ultimate Guitar format: {str(e)}",
                detected_format=self.format_name,
            )

    def _extract_title_artist(
        self, content: str, filename: str
    ) -> tuple[str, str | None]:
        """Extract title and artist from content."""
        artist = None

        # Try "Title by Artist" or "Title - Artist" pattern first
        for pattern in self.TITLE_PATTERNS:
            match = pattern.search(content)
            if match:
                if match.lastindex == 2:
                    # Pattern with both title and artist
                    return match.group(1).strip(), match.group(2).strip()
                else:
                    # Pattern with just title
                    title = match.group(1).strip()
                    break
        else:
            title = None

        # Try separate artist pattern
        artist_match = self.ARTIST_PATTERN.search(content)
        if artist_match:
            artist = artist_match.group(1).strip()

        # If no title found, try first non-metadata, non-chord line
        if not title:
            title = self._infer_title_from_content(content, filename)

        return title, artist

    def _infer_title_from_content(self, content: str, filename: str) -> str:
        """Infer title from first meaningful line or filename."""
        lines = content.split("\n")

        for line in lines[:10]:
            line = line.strip()
            if not line:
                continue

            # Skip metadata lines
            if ":" in line and line.split(":")[0].lower() in [
                "capo", "tuning", "key", "tempo", "bpm", "title", "artist", "song", "by"
            ]:
                continue

            # Skip chord lines
            if self._is_chord_line(line):
                continue

            # Skip section markers
            if self.SECTION_PATTERN.match(line):
                continue

            # Skip tab markers
            if line.lower() in ["[tab]", "[/tab]"]:
                continue

            # Use this line if reasonable length
            if len(line) <= 100:
                return line

        return self._extract_title_from_filename(filename)

    def _extract_capo(self, content: str) -> int | None:
        """Extract capo position."""
        match = self.CAPO_PATTERN.search(content)
        if match:
            try:
                capo = int(match.group(1))
                if 1 <= capo <= 12:
                    return capo
            except ValueError:
                pass
        return None

    def _extract_tuning(self, content: str) -> str | None:
        """Extract tuning info."""
        match = self.TUNING_PATTERN.search(content)
        if match:
            tuning = match.group(1).strip()
            if tuning.lower() != "standard":
                return tuning
        return None

    def _extract_key(self, content: str) -> str | None:
        """Extract key from content."""
        match = self.KEY_PATTERN.search(content)
        if match:
            return match.group(1).strip()
        return None

    def _remove_metadata_lines(self, content: str) -> str:
        """Remove metadata lines from content."""
        lines = content.split("\n")
        result = []

        metadata_prefixes = [
            "capo", "tuning", "key", "tempo", "bpm", "title", "artist", "song", "difficulty"
        ]

        for line in lines:
            stripped = line.strip().lower()

            # Skip metadata lines
            skip = False
            for prefix in metadata_prefixes:
                if stripped.startswith(prefix + ":") or stripped.startswith(prefix + " "):
                    skip = True
                    break

            # Skip "Title by Artist" lines at the start
            if not skip and " by " in line.lower() and lines.index(line) < 3:
                if not self._is_chord_line(line):
                    skip = True

            # Skip tab markers
            if stripped in ["[tab]", "[/tab]"]:
                skip = True

            if not skip:
                result.append(line)

        return "\n".join(result)

    def _is_chord_line(self, line: str) -> bool:
        """Check if a line contains only chords."""
        if not line.strip():
            return False

        if not self.CHORD_LINE_PATTERN.match(line):
            return False

        return bool(self.SINGLE_CHORD_PATTERN.search(line))

    def _convert_to_chordpro(self, content: str) -> str:
        """Convert chord-over-lyrics to ChordPro format."""
        lines = content.split("\n")
        result_lines: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a chord line followed by a lyric line
            if self._is_chord_line(line) and i + 1 < len(lines):
                next_line = lines[i + 1]

                if not self._is_chord_line(next_line) and next_line.strip():
                    # Merge chord line with lyric line
                    merged = self._merge_chord_with_lyric(line, next_line)
                    result_lines.append(merged)
                    i += 2
                    continue

            result_lines.append(line)
            i += 1

        return "\n".join(result_lines)

    def _merge_chord_with_lyric(self, chord_line: str, lyric_line: str) -> str:
        """Merge a chord line with a lyric line into ChordPro format."""
        chords: list[tuple[int, str]] = []

        for match in self.SINGLE_CHORD_PATTERN.finditer(chord_line):
            chords.append((match.start(), match.group(0)))

        if not chords:
            return lyric_line.rstrip()

        result = lyric_line.rstrip()
        offset = 0

        for pos, chord in sorted(chords):
            insert_pos = min(pos + offset, len(result))
            chord_markup = f"[{chord}]"
            result = result[:insert_pos] + chord_markup + result[insert_pos:]
            offset += len(chord_markup)

        return result

    def _extract_plain_lyrics(self, content: str) -> str:
        """Extract plain lyrics without chords."""
        lines = content.split("\n")
        result_lines: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip chord lines
            if self._is_chord_line(line):
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
