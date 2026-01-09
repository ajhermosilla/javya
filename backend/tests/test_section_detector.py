"""Tests for section detection algorithm."""

import pytest

from app.services.import_song.section_detector import (
    SectionDetector,
    SectionType,
)


class TestSectionDetector:
    """Tests for the SectionDetector class."""

    @pytest.fixture
    def detector(self) -> SectionDetector:
        """Create a SectionDetector instance."""
        return SectionDetector()

    def test_normalize_verse_marker_v1(self, detector: SectionDetector):
        """Should normalize [V1] to [Verse 1]."""
        content = """[V1]
First verse lyrics here
Another line"""
        result = detector.detect_sections(content)

        assert "[Verse 1]" in result.normalized_content
        assert result.had_existing_markers is True
        assert len(result.sections) == 1
        assert result.sections[0].section_type == SectionType.VERSE
        assert result.sections[0].number == 1

    def test_normalize_verse_marker_full(self, detector: SectionDetector):
        """Should normalize [Verse] to [Verse 1]."""
        content = """[Verse]
First verse lyrics"""
        result = detector.detect_sections(content)

        assert "[Verse 1]" in result.normalized_content
        assert result.sections[0].section_type == SectionType.VERSE

    def test_normalize_chorus_marker_c(self, detector: SectionDetector):
        """Should normalize [C] to [Chorus 1]."""
        content = """[C]
Chorus lyrics here"""
        result = detector.detect_sections(content)

        # First chorus gets numbered
        assert "[Chorus" in result.normalized_content
        assert result.sections[0].section_type == SectionType.CHORUS

    def test_normalize_chorus_marker_full(self, detector: SectionDetector):
        """Should normalize [Chorus] to [Chorus 1]."""
        content = """[Chorus]
Chorus lyrics here"""
        result = detector.detect_sections(content)

        assert "[Chorus" in result.normalized_content
        assert result.sections[0].section_type == SectionType.CHORUS

    def test_normalize_bridge_marker(self, detector: SectionDetector):
        """Should normalize [B] to [Bridge]."""
        content = """[B]
Bridge lyrics"""
        result = detector.detect_sections(content)

        assert "[Bridge]" in result.normalized_content
        assert result.sections[0].section_type == SectionType.BRIDGE

    def test_normalize_pre_chorus_marker(self, detector: SectionDetector):
        """Should normalize various pre-chorus markers."""
        for marker in ["[P]", "[Pre]", "[Pre-Chorus]", "[PreChorus]"]:
            content = f"""{marker}
Pre-chorus lyrics"""
            result = detector.detect_sections(content)

            assert "[Pre-Chorus]" in result.normalized_content
            assert result.sections[0].section_type == SectionType.PRE_CHORUS

    def test_multiple_sections(self, detector: SectionDetector):
        """Should handle multiple sections."""
        content = """[V1]
First verse lyrics

[C]
Sing along now

[V2]
Second verse lyrics

[C]
Sing along again"""
        result = detector.detect_sections(content)

        assert result.had_existing_markers is True
        assert len(result.sections) == 4

        # Check section types
        assert result.sections[0].section_type == SectionType.VERSE
        assert result.sections[0].number == 1
        assert result.sections[1].section_type == SectionType.CHORUS
        assert result.sections[2].section_type == SectionType.VERSE
        assert result.sections[2].number == 2
        assert result.sections[3].section_type == SectionType.CHORUS

    def test_auto_number_verses(self, detector: SectionDetector):
        """Should auto-number verses when no number provided."""
        content = """[Verse]
First verse

[Verse]
Second verse

[Verse]
Third verse"""
        result = detector.detect_sections(content)

        assert "[Verse 1]" in result.normalized_content
        assert "[Verse 2]" in result.normalized_content
        assert "[Verse 3]" in result.normalized_content

    def test_preserve_explicit_numbers(self, detector: SectionDetector):
        """Should preserve explicit section numbers."""
        content = """[Verse 1]
First verse

[Verse 3]
Third verse (skipped 2)"""
        result = detector.detect_sections(content)

        assert "[Verse 1]" in result.normalized_content
        assert "[Verse 3]" in result.normalized_content
        assert result.sections[0].number == 1
        assert result.sections[1].number == 3

    def test_case_insensitive_markers(self, detector: SectionDetector):
        """Should handle markers in any case."""
        content = """[VERSE]
Upper case verse

[chorus]
Lower case chorus

[BrIdGe]
Mixed case bridge"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.VERSE
        assert result.sections[1].section_type == SectionType.CHORUS
        assert result.sections[2].section_type == SectionType.BRIDGE

    def test_markers_with_colons(self, detector: SectionDetector):
        """Should handle markers with colons."""
        content = """Verse:
Verse with colon

Chorus:
Chorus with colon"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.VERSE
        assert result.sections[1].section_type == SectionType.CHORUS

    def test_empty_content(self, detector: SectionDetector):
        """Should handle empty content."""
        result = detector.detect_sections("")

        assert result.sections == []
        assert result.normalized_content == ""

    def test_whitespace_only(self, detector: SectionDetector):
        """Should handle whitespace-only content."""
        result = detector.detect_sections("   \n\n   ")

        assert result.sections == []


class TestHeuristicDetection:
    """Tests for heuristic section detection (no markers)."""

    @pytest.fixture
    def detector(self) -> SectionDetector:
        """Create a SectionDetector instance."""
        return SectionDetector()

    def test_detect_chorus_from_repetition(self, detector: SectionDetector):
        """Should detect chorus from repeated blocks."""
        content = """First verse content here
These are unique lyrics

This is the chorus line
It repeats exactly

Second verse content
Different from the first

This is the chorus line
It repeats exactly"""
        result = detector.detect_sections(content)

        assert result.had_existing_markers is False

        # Find chorus sections
        chorus_sections = [
            s for s in result.sections if s.section_type == SectionType.CHORUS
        ]
        assert len(chorus_sections) >= 1
        assert all(s.is_auto_detected for s in result.sections)

    def test_single_block_is_verse(self, detector: SectionDetector):
        """Should treat single block as verse."""
        content = """Just one block of lyrics
Without any blank lines
All together"""
        result = detector.detect_sections(content)

        assert result.had_existing_markers is False
        assert len(result.sections) == 1
        assert result.sections[0].section_type == SectionType.VERSE
        assert result.sections[0].number == 1
        assert result.sections[0].is_auto_detected is True

    def test_unique_blocks_are_verses(self, detector: SectionDetector):
        """Should treat unique non-repeating blocks as verses."""
        content = """First verse here
With some lines

Second verse here
Also with lines

Third verse content
More unique content"""
        result = detector.detect_sections(content)

        assert result.had_existing_markers is False
        # All unique blocks should be verses
        verse_sections = [
            s for s in result.sections if s.section_type == SectionType.VERSE
        ]
        assert len(verse_sections) == 3

    def test_auto_detected_sections_have_confidence(self, detector: SectionDetector):
        """Auto-detected sections should have confidence < 1.0."""
        content = """First verse

Chorus content
Repeated later

Second verse

Chorus content
Repeated later"""
        result = detector.detect_sections(content)

        assert all(s.confidence < 1.0 for s in result.sections)

    def test_normalized_content_includes_markers(self, detector: SectionDetector):
        """Normalized content should include section markers."""
        content = """First verse lyrics

Chorus lyrics here

Second verse lyrics"""
        result = detector.detect_sections(content)

        # Should have markers added
        assert "[Verse" in result.normalized_content or "[Chorus" in result.normalized_content


class TestMarkerPatterns:
    """Tests for various marker pattern formats."""

    @pytest.fixture
    def detector(self) -> SectionDetector:
        """Create a SectionDetector instance."""
        return SectionDetector()

    def test_brackets_required(self, detector: SectionDetector):
        """Markers should work with or without brackets."""
        # Without brackets but with colon
        content1 = """Verse:
Content"""
        result1 = detector.detect_sections(content1)
        assert result1.sections[0].section_type == SectionType.VERSE

        # With brackets
        content2 = """[Verse]
Content"""
        result2 = detector.detect_sections(content2)
        assert result2.sections[0].section_type == SectionType.VERSE

    def test_refrain_is_chorus(self, detector: SectionDetector):
        """Refrain should be treated as chorus."""
        content = """[Refrain]
Refrain lyrics"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.CHORUS

    def test_hook_is_chorus(self, detector: SectionDetector):
        """Hook should be treated as chorus."""
        content = """[Hook]
Hook lyrics"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.CHORUS

    def test_tag_section(self, detector: SectionDetector):
        """Should recognize tag sections."""
        content = """[Tag]
Tag lyrics"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.TAG

    def test_intro_section(self, detector: SectionDetector):
        """Should recognize intro sections."""
        content = """[Intro]
Intro content"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.INTRO

    def test_outro_section(self, detector: SectionDetector):
        """Should recognize outro sections."""
        content = """[Outro]
Outro content"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.OUTRO

    def test_interlude_section(self, detector: SectionDetector):
        """Should recognize interlude sections."""
        content = """[Interlude]
Interlude content"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.INTERLUDE

    def test_instrumental_section(self, detector: SectionDetector):
        """Should recognize instrumental sections."""
        content = """[Instrumental]
"""
        result = detector.detect_sections(content)

        assert result.sections[0].section_type == SectionType.INSTRUMENTAL
