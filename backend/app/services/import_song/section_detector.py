"""Section detection and normalization for song lyrics.

Detects song sections (verse, chorus, bridge, etc.) either from existing
markers or using heuristics based on repetition patterns.
"""

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from enum import Enum


class SectionType(str, Enum):
    """Standard section types."""

    VERSE = "Verse"
    CHORUS = "Chorus"
    BRIDGE = "Bridge"
    PRE_CHORUS = "Pre-Chorus"
    TAG = "Tag"
    INTRO = "Intro"
    OUTRO = "Outro"
    INTERLUDE = "Interlude"
    INSTRUMENTAL = "Instrumental"
    ENDING = "Ending"
    UNKNOWN = "Section"


@dataclass
class DetectedSection:
    """A detected section in the lyrics."""

    section_type: SectionType
    number: int | None  # e.g., 1 for "Verse 1"
    start_line: int
    end_line: int
    content: str
    confidence: float = 1.0  # 0.0 to 1.0
    is_auto_detected: bool = False  # True if no marker existed


@dataclass
class SectionDetectionResult:
    """Result of section detection."""

    sections: list[DetectedSection] = field(default_factory=list)
    normalized_content: str = ""
    had_existing_markers: bool = False


class SectionDetector:
    """Detects and normalizes song sections.

    Can identify sections from explicit markers like [Verse], [Chorus], etc.
    and can also auto-detect sections using heuristics when no markers exist.
    """

    # Pattern to match existing section markers
    # Matches: [Verse], [V1], [Chorus], [C], [Bridge], etc.
    SECTION_MARKER_PATTERN = re.compile(
        r"^\s*\[?\s*"
        r"(V(?:erse)?|C(?:horus)?|B(?:ridge)?|P(?:re)?(?:-?C(?:horus)?)?|"
        r"Tag|Intro|Outro|Interlude|Instrumental|Ending|Coda|Refrain|Hook|"
        r"Verse|Chorus|Bridge|Pre-Chorus|PreChorus|Pre Chorus)"
        r"(?:\s*(\d+))?\s*\]?\s*:?\s*$",
        re.IGNORECASE,
    )

    # Mapping from marker text to section type
    SECTION_ALIASES: dict[str, SectionType] = {
        "v": SectionType.VERSE,
        "verse": SectionType.VERSE,
        "c": SectionType.CHORUS,
        "chorus": SectionType.CHORUS,
        "refrain": SectionType.CHORUS,
        "hook": SectionType.CHORUS,
        "b": SectionType.BRIDGE,
        "bridge": SectionType.BRIDGE,
        "p": SectionType.PRE_CHORUS,
        "pc": SectionType.PRE_CHORUS,
        "pre": SectionType.PRE_CHORUS,
        "pre-c": SectionType.PRE_CHORUS,
        "pre-chorus": SectionType.PRE_CHORUS,
        "prechorus": SectionType.PRE_CHORUS,
        "pre chorus": SectionType.PRE_CHORUS,
        "tag": SectionType.TAG,
        "coda": SectionType.TAG,
        "ending": SectionType.ENDING,
        "intro": SectionType.INTRO,
        "outro": SectionType.OUTRO,
        "interlude": SectionType.INTERLUDE,
        "instrumental": SectionType.INSTRUMENTAL,
    }

    # Minimum similarity threshold for chorus detection (0.0 to 1.0)
    CHORUS_SIMILARITY_THRESHOLD = 0.85

    def detect_sections(self, content: str) -> SectionDetectionResult:
        """Detect sections in song content.

        Args:
            content: Song lyrics content (with or without section markers)

        Returns:
            SectionDetectionResult with sections and normalized content
        """
        if not content or not content.strip():
            return SectionDetectionResult()

        lines = content.split("\n")

        # First, try to find existing markers
        markers = self._find_existing_markers(lines)

        if markers:
            # Use existing markers - normalize them
            return self._process_existing_markers(lines, markers)
        else:
            # No markers found - try heuristic detection
            return self._detect_sections_heuristically(content)

    def _find_existing_markers(
        self, lines: list[str]
    ) -> list[tuple[int, SectionType, int | None]]:
        """Find existing section markers in content.

        Args:
            lines: List of content lines

        Returns:
            List of (line_index, section_type, number) tuples
        """
        markers: list[tuple[int, SectionType, int | None]] = []

        for i, line in enumerate(lines):
            match = self.SECTION_MARKER_PATTERN.match(line)
            if match:
                section_text = match.group(1).lower().replace(" ", "")
                number_text = match.group(2)

                section_type = self.SECTION_ALIASES.get(
                    section_text, SectionType.UNKNOWN
                )
                number = int(number_text) if number_text else None

                markers.append((i, section_type, number))

        return markers

    def _process_existing_markers(
        self, lines: list[str], markers: list[tuple[int, SectionType, int | None]]
    ) -> SectionDetectionResult:
        """Process content with existing markers, normalizing them.

        Args:
            lines: List of content lines
            markers: List of (line_index, section_type, number) tuples

        Returns:
            SectionDetectionResult with normalized markers
        """
        sections: list[DetectedSection] = []
        normalized_lines = lines.copy()

        # Track section numbers for auto-numbering
        section_counts: dict[SectionType, int] = {}

        for i, (line_idx, section_type, number) in enumerate(markers):
            # Determine section number
            if number is None and section_type in (
                SectionType.VERSE,
                SectionType.CHORUS,
            ):
                # Auto-number verses and choruses
                section_counts[section_type] = section_counts.get(section_type, 0) + 1
                number = section_counts[section_type]
            elif number is not None:
                # Track explicit numbers
                section_counts[section_type] = max(
                    section_counts.get(section_type, 0), number
                )

            # Find end line (next marker or end of content)
            if i + 1 < len(markers):
                end_line = markers[i + 1][0]
            else:
                end_line = len(lines)

            # Extract section content (excluding marker line)
            section_content = "\n".join(lines[line_idx + 1 : end_line]).strip()

            # Create normalized marker
            normalized_marker = self._format_marker(section_type, number)
            normalized_lines[line_idx] = normalized_marker

            sections.append(
                DetectedSection(
                    section_type=section_type,
                    number=number,
                    start_line=line_idx,
                    end_line=end_line,
                    content=section_content,
                    confidence=1.0,
                    is_auto_detected=False,
                )
            )

        return SectionDetectionResult(
            sections=sections,
            normalized_content="\n".join(normalized_lines),
            had_existing_markers=True,
        )

    def _detect_sections_heuristically(self, content: str) -> SectionDetectionResult:
        """Detect sections using heuristics when no markers exist.

        Heuristics:
        - Split into blocks by blank lines
        - Find repeated blocks (potential choruses)
        - First unique block is verse 1
        - Assign other blocks based on patterns

        Args:
            content: Full lyrics content

        Returns:
            SectionDetectionResult with auto-detected sections
        """
        # Split into blocks
        blocks = self._split_into_blocks(content)

        if not blocks:
            return SectionDetectionResult(normalized_content=content)

        if len(blocks) == 1:
            # Single block - probably all verse
            return SectionDetectionResult(
                sections=[
                    DetectedSection(
                        section_type=SectionType.VERSE,
                        number=1,
                        start_line=0,
                        end_line=content.count("\n") + 1,
                        content=blocks[0]["content"],
                        confidence=0.5,
                        is_auto_detected=True,
                    )
                ],
                normalized_content=f"[Verse 1]\n{content}",
                had_existing_markers=False,
            )

        # Find repeated blocks (potential choruses)
        repeated_indices = self._find_repeated_blocks(blocks)

        sections: list[DetectedSection] = []
        normalized_parts: list[str] = []
        verse_num = 0
        chorus_num = 0

        for i, block in enumerate(blocks):
            if i in repeated_indices:
                # This is a repeated block - likely chorus
                chorus_num += 1
                section_type = SectionType.CHORUS
                number = chorus_num if chorus_num > 1 else None
                confidence = 0.8  # High confidence for repeated blocks
            else:
                # Unique block - likely verse
                verse_num += 1
                section_type = SectionType.VERSE
                number = verse_num
                confidence = 0.6

            marker = self._format_marker(section_type, number)
            normalized_parts.append(marker)
            normalized_parts.append(block["content"])

            sections.append(
                DetectedSection(
                    section_type=section_type,
                    number=number,
                    start_line=block["start_line"],
                    end_line=block["end_line"],
                    content=block["content"],
                    confidence=confidence,
                    is_auto_detected=True,
                )
            )

        return SectionDetectionResult(
            sections=sections,
            normalized_content="\n\n".join(normalized_parts),
            had_existing_markers=False,
        )

    def _split_into_blocks(self, content: str) -> list[dict]:
        """Split content into blocks separated by blank lines.

        Args:
            content: Full lyrics content

        Returns:
            List of dicts with 'content', 'start_line', 'end_line' keys
        """
        lines = content.split("\n")
        blocks: list[dict] = []
        current_block_lines: list[str] = []
        block_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                # Blank line - end of block
                if current_block_lines:
                    blocks.append(
                        {
                            "content": "\n".join(current_block_lines),
                            "start_line": block_start,
                            "end_line": i,
                        }
                    )
                    current_block_lines = []
            else:
                if not current_block_lines:
                    block_start = i
                current_block_lines.append(line)

        # Don't forget the last block
        if current_block_lines:
            blocks.append(
                {
                    "content": "\n".join(current_block_lines),
                    "start_line": block_start,
                    "end_line": len(lines),
                }
            )

        return blocks

    def _find_repeated_blocks(self, blocks: list[dict]) -> set[int]:
        """Find indices of blocks that repeat (potential choruses).

        Args:
            blocks: List of block dicts

        Returns:
            Set of indices that are repeated blocks
        """
        repeated: set[int] = set()
        n = len(blocks)

        for i in range(n):
            for j in range(i + 1, n):
                similarity = self._calculate_similarity(
                    blocks[i]["content"], blocks[j]["content"]
                )
                if similarity >= self.CHORUS_SIMILARITY_THRESHOLD:
                    repeated.add(i)
                    repeated.add(j)

        return repeated

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text blocks.

        Args:
            text1: First text block
            text2: Second text block

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        # Normalize texts for comparison
        norm1 = self._normalize_for_comparison(text1)
        norm2 = self._normalize_for_comparison(text2)

        return SequenceMatcher(None, norm1, norm2).ratio()

    def _normalize_for_comparison(self, text: str) -> str:
        """Normalize text for comparison (ignore case, extra whitespace).

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Remove chord markers like [G], [Am], etc.
        text = re.sub(r"\[[A-Ga-g][^\]]*\]", "", text)
        # Lowercase
        text = text.lower()
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _format_marker(self, section_type: SectionType, number: int | None) -> str:
        """Format a normalized section marker.

        Args:
            section_type: Type of section
            number: Optional section number

        Returns:
            Formatted marker string like "[Verse 1]" or "[Chorus]"
        """
        if number is not None:
            return f"[{section_type.value} {number}]"
        return f"[{section_type.value}]"
