"""Parser for OpenSong XML format files."""

import re
from xml.etree import ElementTree as ET

from .base import BaseSongParser, ParseResult


class OpenSongParser(BaseSongParser):
    """Parser for OpenSong XML format.

    OpenSong uses a simpler XML structure than OpenLyrics.

    Structure:
    - <song> root element
    - Direct child elements for metadata: <title>, <author>, <key>, etc.
    - <lyrics> contains text with dot-prefixed chord lines

    Chord format in lyrics:
    - Lines starting with "." contain chords
    - Chords are space-aligned above lyrics
    - Section markers in brackets: [V], [C], [B]

    Example:
    <song>
      <title>Amazing Grace</title>
      <author>John Newton</author>
      <key>G</key>
      <lyrics>
    [V]
    .G       D7      G
    Amazing grace, how sweet the sound
      </lyrics>
    </song>
    """

    format_name = "opensong"

    def can_parse(self, content: str, filename: str) -> bool:
        """Check for OpenSong XML format.

        Detection:
        1. Valid XML with <song> root
        2. Has <lyrics> element (distinguishes from OpenLyrics)
        3. Does NOT have OpenLyrics namespace
        """
        content = content.strip()

        # Must be XML
        if not (content.startswith("<?xml") or content.startswith("<")):
            return False

        # Must not be OpenLyrics
        if "openlyrics" in content.lower():
            return False

        # Check for OpenSong structure
        return "<song>" in content and "<lyrics>" in content

    def parse(self, content: str, filename: str) -> ParseResult:
        """Parse OpenSong XML content."""
        try:
            root = ET.fromstring(content)

            # Extract metadata from direct child elements
            title = self._get_element_text(root, "title")
            artist = self._get_element_text(root, "author") or self._get_element_text(
                root, "artist"
            )
            key = self._get_element_text(root, "key")
            tempo_str = self._get_element_text(root, "tempo")

            # Parse tempo
            tempo = None
            if tempo_str:
                try:
                    tempo_val = int(tempo_str)
                    if 20 <= tempo_val <= 300:
                        tempo = tempo_val
                except ValueError:
                    pass

            # Collect notes
            notes_parts: list[str] = []

            copyright_text = self._get_element_text(root, "copyright")
            if copyright_text:
                notes_parts.append(f"Copyright: {copyright_text}")

            ccli = self._get_element_text(root, "ccli")
            if ccli:
                notes_parts.append(f"CCLI: {ccli}")

            theme = self._get_element_text(root, "theme")
            if theme:
                notes_parts.append(f"Theme: {theme}")

            alt_theme = self._get_element_text(root, "alttheme")
            if alt_theme:
                notes_parts.append(f"Alt Theme: {alt_theme}")

            # Extract lyrics
            lyrics_elem = root.find("lyrics")
            raw_lyrics = lyrics_elem.text if lyrics_elem is not None else ""

            lyrics, chordpro = self._convert_opensong_to_chordpro(raw_lyrics or "")

            # Use filename if no title
            if not title:
                title = self._extract_title_from_filename(filename)

            notes = "\n".join(notes_parts) if notes_parts else None

            return ParseResult(
                success=True,
                song_data=self._build_song_data(
                    name=title,
                    artist=artist,
                    original_key=self._normalize_key(key),
                    tempo_bpm=tempo,
                    lyrics=lyrics,
                    chordpro_chart=chordpro if chordpro != lyrics else None,
                    notes=notes,
                ),
                detected_format=self.format_name,
            )

        except ET.ParseError as e:
            return ParseResult(
                success=False,
                error=f"Invalid XML: {str(e)}",
                detected_format=self.format_name,
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Failed to parse OpenSong: {str(e)}",
                detected_format=self.format_name,
            )

    def _get_element_text(self, root: ET.Element, tag: str) -> str | None:
        """Get text content of a child element."""
        elem = root.find(tag)
        if elem is not None and elem.text:
            return elem.text.strip()
        return None

    def _convert_opensong_to_chordpro(self, raw: str) -> tuple[str, str]:
        """Convert OpenSong lyrics to plain lyrics and ChordPro format.

        OpenSong format:
        - Lines starting with "." are chord lines
        - Lines starting with "[" are section markers
        - Other lines are lyrics
        - Chords are position-aligned above lyrics

        Returns:
            Tuple of (plain_lyrics, chordpro_chart)
        """
        lines = raw.split("\n")
        plain_lines: list[str] = []
        chordpro_lines: list[str] = []
        has_chords = False

        i = 0
        while i < len(lines):
            line = lines[i].rstrip()

            # Section marker like [V], [C], [B]
            if line.strip().startswith("[") and line.strip().endswith("]"):
                section = line.strip()[1:-1]
                section_name = self._format_section_name(section)
                plain_lines.append(f"[{section_name}]")
                chordpro_lines.append(f"[{section_name}]")
                i += 1
                continue

            # Chord line (starts with ".")
            if line.startswith("."):
                chord_line = line[1:]  # Remove leading dot
                has_chords = True

                # Look for next lyric line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].rstrip()

                    # Skip if next line is also a chord line or section marker
                    if not next_line.startswith(".") and not (
                        next_line.strip().startswith("[")
                        and next_line.strip().endswith("]")
                    ):
                        # Merge chord line with lyric line
                        merged = self._merge_chords_with_lyrics(chord_line, next_line)
                        plain_lines.append(next_line.strip())
                        chordpro_lines.append(merged)
                        i += 2
                        continue

                # Chord line without lyrics (instrumental)
                chords = self._extract_chords_from_line(chord_line)
                if chords:
                    chord_str = " ".join(f"[{c}]" for c in chords)
                    chordpro_lines.append(chord_str)
                i += 1
                continue

            # Regular lyric line or empty line
            if line.strip():
                plain_lines.append(line.strip())
                chordpro_lines.append(line.strip())
            else:
                plain_lines.append("")
                chordpro_lines.append("")

            i += 1

        plain_text = "\n".join(plain_lines).strip()
        chordpro_text = "\n".join(chordpro_lines).strip() if has_chords else plain_text

        return plain_text, chordpro_text

    def _merge_chords_with_lyrics(self, chord_line: str, lyric_line: str) -> str:
        """Merge a chord line with a lyric line into ChordPro format.

        Chords are position-aligned in OpenSong, so we insert [chord]
        at the corresponding position in the lyrics.
        """
        # Find chord positions and names
        chords = self._parse_chord_positions(chord_line)

        if not chords:
            return lyric_line.strip()

        # Build result by inserting chords at positions
        result = lyric_line
        offset = 0

        for pos, chord in sorted(chords):
            # Adjust position for previously inserted chords
            insert_pos = min(pos + offset, len(result))
            chord_markup = f"[{chord}]"
            result = result[:insert_pos] + chord_markup + result[insert_pos:]
            offset += len(chord_markup)

        return result.strip()

    def _parse_chord_positions(self, chord_line: str) -> list[tuple[int, str]]:
        """Parse chord positions from a chord line.

        Returns list of (position, chord_name) tuples.
        """
        chords: list[tuple[int, str]] = []

        # Find chords using regex
        chord_pattern = re.compile(
            r"([A-G][#b♯♭]?"
            r"(?:maj|min|m|dim|aug|sus[24]?|add[29]?|7|9|11|13|6)?)"
            r"(?:/([A-G][#b♯♭]?))?"
        )

        for match in chord_pattern.finditer(chord_line):
            pos = match.start()
            chord = match.group(0)
            chords.append((pos, chord))

        return chords

    def _extract_chords_from_line(self, line: str) -> list[str]:
        """Extract chord names from a line."""
        chord_pattern = re.compile(
            r"([A-G][#b♯♭]?"
            r"(?:maj|min|m|dim|aug|sus[24]?|add[29]?|7|9|11|13|6)?)"
            r"(?:/([A-G][#b♯♭]?))?"
        )
        return [match.group(0) for match in chord_pattern.finditer(line)]

    def _format_section_name(self, name: str) -> str:
        """Format section marker to readable name.

        Examples:
        - "V" or "V1" -> "Verse 1"
        - "C" -> "Chorus"
        - "B" -> "Bridge"
        """
        section_map = {
            "V": "Verse",
            "C": "Chorus",
            "B": "Bridge",
            "P": "Pre-Chorus",
            "E": "Ending",
            "I": "Intro",
            "O": "Outro",
            "T": "Tag",
        }

        name = name.strip().upper()

        # Check for format like "V1", "C2"
        if len(name) >= 1:
            letter = name[0]
            number = name[1:] if len(name) > 1 else ""

            if letter in section_map:
                result = section_map[letter]
                if number and number.isdigit():
                    result += f" {number}"
                return result

        return name
