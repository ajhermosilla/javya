"""Parser for OpenLyrics/OpenLP XML format files."""

import re
from xml.etree import ElementTree as ET

from .base import BaseSongParser, ParseResult


class OpenLyricsParser(BaseSongParser):
    """Parser for OpenLyrics/OpenLP XML format.

    OpenLyrics is an XML format used by OpenLP and other worship software.

    Structure:
    - <song> root element with OpenLyrics namespace
    - <properties> contains metadata (titles, authors, key, tempo, themes)
    - <lyrics> contains verses with optional chord annotations

    Example:
    <song xmlns="http://openlyrics.info/namespace/2009/song">
      <properties>
        <titles><title>Amazing Grace</title></titles>
        <authors><author>John Newton</author></authors>
        <key>G</key>
        <tempo type="bpm">80</tempo>
      </properties>
      <lyrics>
        <verse name="v1">
          <lines>Amazing grace, how sweet the sound</lines>
        </verse>
      </lyrics>
    </song>
    """

    format_name = "openlyrics"

    # OpenLyrics namespace
    NAMESPACE = "http://openlyrics.info/namespace/2009/song"
    NS = {"ol": NAMESPACE}

    def can_parse(self, content: str, filename: str) -> bool:
        """Check for OpenLyrics XML format.

        Detection:
        1. Content is valid XML
        2. Contains OpenLyrics namespace or structure
        """
        content = content.strip()

        # Must look like XML
        if not (content.startswith("<?xml") or content.startswith("<")):
            return False

        # Check for OpenLyrics namespace
        if "openlyrics" in content.lower():
            return True

        # Check for OpenLyrics-style structure
        if "<song" in content and "<properties>" in content:
            return True

        return False

    def parse(self, content: str, filename: str) -> ParseResult:
        """Parse OpenLyrics XML content."""
        try:
            # Parse XML
            root = ET.fromstring(content)

            # Determine if using namespace
            use_ns = "openlyrics" in content.lower()

            # Find properties section
            props = self._find_element(root, "properties", use_ns)

            title = None
            artist = None
            key = None
            tempo = None
            notes_parts: list[str] = []

            if props is not None:
                # Title
                titles = self._find_element(props, "titles", use_ns)
                if titles is not None:
                    title_elem = self._find_element(titles, "title", use_ns)
                    if title_elem is not None and title_elem.text:
                        title = title_elem.text.strip()

                # Author/Artist
                authors = self._find_element(props, "authors", use_ns)
                if authors is not None:
                    for author in self._find_all_elements(authors, "author", use_ns):
                        if author.text:
                            author_type = author.get("type", "")
                            if not artist and author_type in ("", "words", "lyrics"):
                                artist = author.text.strip()
                            elif author_type == "music":
                                notes_parts.append(f"Music by: {author.text.strip()}")

                # Key
                key_elem = self._find_element(props, "key", use_ns)
                if key_elem is not None and key_elem.text:
                    key = key_elem.text.strip()

                # Tempo
                tempo_elem = self._find_element(props, "tempo", use_ns)
                if tempo_elem is not None and tempo_elem.text:
                    try:
                        tempo_val = int(tempo_elem.text.strip())
                        if 20 <= tempo_val <= 300:
                            tempo = tempo_val
                    except ValueError:
                        pass

                # Copyright
                copyright_elem = self._find_element(props, "copyright", use_ns)
                if copyright_elem is not None and copyright_elem.text:
                    notes_parts.append(f"Copyright: {copyright_elem.text.strip()}")

                # CCLI number
                ccli_elem = self._find_element(props, "ccliNo", use_ns)
                if ccli_elem is not None and ccli_elem.text:
                    notes_parts.append(f"CCLI: {ccli_elem.text.strip()}")

                # Comments
                comments = self._find_element(props, "comments", use_ns)
                if comments is not None and comments.text:
                    notes_parts.append(comments.text.strip())

            # Extract lyrics
            lyrics_elem = self._find_element(root, "lyrics", use_ns)
            lyrics, chordpro = self._extract_lyrics(lyrics_elem, use_ns)

            # Normalize sections in lyrics
            normalized_lyrics, sections_normalized = self._normalize_sections(lyrics)

            # Extract chords and detect key from ChordPro content
            chords = self._extract_chords(chordpro) if chordpro else []
            detected_key, key_confidence = self._detect_key_from_chords(chords)

            # Use filename if no title found
            if not title:
                title = self._extract_title_from_filename(filename)

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
                    chordpro_chart=chordpro if chordpro else None,
                    notes=notes,
                ),
                detected_format=self.format_name,
                specified_key=specified_key,
                detected_key=detected_key,
                key_confidence=key_confidence,
                sections_normalized=sections_normalized,
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
                error=f"Failed to parse OpenLyrics: {str(e)}",
                detected_format=self.format_name,
            )

    def _find_element(
        self, parent: ET.Element, tag: str, use_ns: bool
    ) -> ET.Element | None:
        """Find a child element, handling namespace."""
        if use_ns:
            elem = parent.find(f"ol:{tag}", self.NS)
            if elem is not None:
                return elem
        return parent.find(tag)

    def _find_all_elements(
        self, parent: ET.Element, tag: str, use_ns: bool
    ) -> list[ET.Element]:
        """Find all child elements, handling namespace."""
        if use_ns:
            elems = parent.findall(f"ol:{tag}", self.NS)
            if elems:
                return elems
        return parent.findall(tag)

    def _extract_lyrics(
        self, lyrics_elem: ET.Element | None, use_ns: bool
    ) -> tuple[str, str]:
        """Extract plain lyrics and ChordPro from OpenLyrics lyrics section.

        Returns:
            Tuple of (plain_lyrics, chordpro_chart)
        """
        if lyrics_elem is None:
            return "", ""

        plain_lines: list[str] = []
        chordpro_lines: list[str] = []
        has_chords = False

        # Process verses
        verses = self._find_all_elements(lyrics_elem, "verse", use_ns)
        for verse in verses:
            verse_name = verse.get("name", "")

            # Add section header
            if verse_name:
                section = self._format_section_name(verse_name)
                chordpro_lines.append(f"[{section}]")

            # Process lines
            lines_elem = self._find_element(verse, "lines", use_ns)
            if lines_elem is not None:
                verse_text, verse_chordpro, verse_has_chords = self._process_lines(
                    lines_elem
                )
                plain_lines.append(verse_text)
                chordpro_lines.append(verse_chordpro)
                if verse_has_chords:
                    has_chords = True

            # Add blank line between verses
            plain_lines.append("")
            chordpro_lines.append("")

        plain_text = "\n".join(plain_lines).strip()
        chordpro_text = "\n".join(chordpro_lines).strip() if has_chords else ""

        return plain_text, chordpro_text

    def _process_lines(self, lines_elem: ET.Element) -> tuple[str, str, bool]:
        """Process a <lines> element, extracting text and chords.

        Returns:
            Tuple of (plain_text, chordpro_text, has_chords)
        """
        plain_parts: list[str] = []
        chordpro_parts: list[str] = []
        has_chords = False

        # Get the full text content including nested elements
        def process_element(elem: ET.Element) -> tuple[str, str]:
            nonlocal has_chords
            plain = ""
            chordpro = ""

            # Handle chord elements
            if elem.tag.endswith("chord") or elem.tag == "chord":
                has_chords = True
                root = elem.get("root", "")
                chord_type = elem.get("type", "")
                bass = elem.get("bass", "")

                chord = root + chord_type
                if bass:
                    chord += f"/{bass}"

                chordpro = f"[{chord}]"
                # Chord has no text contribution to plain lyrics

            # Handle line breaks
            elif elem.tag.endswith("br") or elem.tag == "br":
                plain = "\n"
                chordpro = "\n"

            # Add text before children
            if elem.text:
                plain += elem.text
                chordpro += elem.text

            # Process children
            for child in elem:
                child_plain, child_chordpro = process_element(child)
                plain += child_plain
                chordpro += child_chordpro

                # Add tail text after each child
                if child.tail:
                    plain += child.tail
                    chordpro += child.tail

            return plain, chordpro

        plain, chordpro = process_element(lines_elem)

        return plain.strip(), chordpro.strip(), has_chords

    def _format_section_name(self, name: str) -> str:
        """Format verse name to readable section header.

        Examples:
        - "v1" -> "Verse 1"
        - "c1" -> "Chorus 1"
        - "b1" -> "Bridge 1"
        - "p1" -> "Pre-Chorus 1"
        """
        section_map = {
            "v": "Verse",
            "c": "Chorus",
            "b": "Bridge",
            "p": "Pre-Chorus",
            "e": "Ending",
            "i": "Intro",
            "o": "Outro",
            "t": "Tag",
        }

        # Parse format like "v1", "c2", etc.
        match = re.match(r"([a-z])(\d*)", name.lower())
        if match:
            section_type = match.group(1)
            section_num = match.group(2)

            if section_type in section_map:
                result = section_map[section_type]
                if section_num:
                    result += f" {section_num}"
                return result

        return name
