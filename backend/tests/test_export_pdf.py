"""Unit tests for PDF export service."""

import pytest

from app.services.export_pdf import (
    extract_section_name,
    is_section_header,
    parse_chordpro_to_html,
    parse_directive,
    render_chord_line,
    strip_chordpro_for_summary,
)


class TestChordProParser:
    """Tests for ChordPro parsing functions."""

    def test_parse_simple_chord_line(self) -> None:
        """Test parsing a simple line with chords."""
        input_text = "[G]Amazing [G7]grace"
        result = parse_chordpro_to_html(input_text)
        assert "chord" in result
        assert ">G<" in result
        assert ">G7<" in result
        assert "Amazing" in result

    def test_parse_section_header(self) -> None:
        """Test parsing section headers."""
        input_text = "[Verse 1]\nSome lyrics here"
        result = parse_chordpro_to_html(input_text)
        assert "section-header" in result
        assert "Verse 1" in result

    def test_parse_multiple_sections(self) -> None:
        """Test parsing multiple sections."""
        input_text = "[Verse 1]\nFirst verse\n\n[Chorus]\nChorus lyrics"
        result = parse_chordpro_to_html(input_text)
        assert "Verse 1" in result
        assert "Chorus" in result
        assert "First verse" in result

    def test_is_section_header_true(self) -> None:
        """Test section header detection."""
        assert is_section_header("[Verse 1]") is True
        assert is_section_header("[Chorus]") is True
        assert is_section_header("[Bridge]") is True
        assert is_section_header("[Pre-Chorus]") is True
        assert is_section_header("[Outro]") is True

    def test_is_section_header_false_for_chords(self) -> None:
        """Test that chord annotations are not detected as headers."""
        assert is_section_header("[Am]") is False
        assert is_section_header("[G7]") is False
        assert is_section_header("[Cmaj7]") is False
        assert is_section_header("[F#m]") is False
        assert is_section_header("[Bb]") is False
        assert is_section_header("[A]") is False

    def test_is_section_header_false_for_partial(self) -> None:
        """Test that incomplete brackets return False."""
        assert is_section_header("[Verse 1") is False
        assert is_section_header("Verse 1]") is False
        assert is_section_header("Verse 1") is False

    def test_extract_section_name(self) -> None:
        """Test section name extraction."""
        assert extract_section_name("[Verse 1]") == "Verse 1"
        assert extract_section_name("[Chorus]") == "Chorus"
        assert extract_section_name("[Pre-Chorus]") == "Pre-Chorus"

    def test_strip_chordpro_for_summary(self) -> None:
        """Test stripping ChordPro annotations."""
        input_text = "[G]Amazing [G7]grace, how [C]sweet"
        result = strip_chordpro_for_summary(input_text)
        assert result == "Amazing grace, how sweet"
        assert "[G]" not in result
        assert "[G7]" not in result
        assert "[C]" not in result

    def test_strip_chordpro_empty_input(self) -> None:
        """Test stripping with empty input."""
        assert strip_chordpro_for_summary(None) == ""
        assert strip_chordpro_for_summary("") == ""

    def test_parse_empty_input(self) -> None:
        """Test parsing empty or None input."""
        assert parse_chordpro_to_html(None) == ""
        assert parse_chordpro_to_html("") == ""

    def test_parse_directive_comment(self) -> None:
        """Test parsing comment directive."""
        result = parse_directive("{comment: Play softly}")
        assert result is not None
        assert "comment" in result
        assert "Play softly" in result

    def test_parse_directive_short_comment(self) -> None:
        """Test parsing short comment directive."""
        result = parse_directive("{c: Instrumental}")
        assert result is not None
        assert "comment" in result
        assert "Instrumental" in result

    def test_parse_directive_title(self) -> None:
        """Test parsing title directive."""
        result = parse_directive("{title: Amazing Grace}")
        assert result is not None
        assert "Amazing Grace" in result

    def test_parse_directive_invalid(self) -> None:
        """Test parsing invalid directive returns None."""
        assert parse_directive("{invalid}") is None
        assert parse_directive("not a directive") is None

    def test_render_chord_line_basic(self) -> None:
        """Test rendering a basic chord line."""
        result = render_chord_line("[G]Hello [Am]world")
        assert "chord-line" in result
        assert ">G<" in result
        assert ">Am<" in result
        assert "Hello" in result
        assert "world" in result

    def test_render_chord_line_escapes_html(self) -> None:
        """Test that HTML entities are escaped."""
        result = render_chord_line("[G]Hello <world> & friends")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result

    def test_parse_preserves_empty_lines(self) -> None:
        """Test that empty lines are preserved."""
        input_text = "Line 1\n\nLine 2"
        result = parse_chordpro_to_html(input_text)
        assert "empty-line" in result

    def test_parse_plain_lyrics(self) -> None:
        """Test parsing plain lyrics without chords."""
        input_text = "Just plain lyrics\nNo chords here"
        result = parse_chordpro_to_html(input_text)
        assert "lyric-line" in result
        assert "Just plain lyrics" in result
        assert "No chords here" in result

    def test_parse_complex_chords(self) -> None:
        """Test parsing complex chord names."""
        input_text = "[Cmaj7]Some [F#m7b5]complex [Bbsus4]chords"
        result = parse_chordpro_to_html(input_text)
        assert "Cmaj7" in result
        assert "F#m7b5" in result
        assert "Bbsus4" in result
