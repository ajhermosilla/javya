"""Tests for song import parsers."""

from pathlib import Path

import pytest

from app.enums import MusicalKey
from app.services.import_song import detect_and_parse, ParseResult
from app.services.import_song.chordpro_parser import ChordProParser
from app.services.import_song.openlyrics_parser import OpenLyricsParser
from app.services.import_song.opensong_parser import OpenSongParser
from app.services.import_song.plaintext_parser import PlainTextParser


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "import_samples"


class TestChordProParser:
    """Tests for ChordPro format parser."""

    def test_can_parse_by_extension(self):
        """Should detect ChordPro by file extension."""
        parser = ChordProParser()
        assert parser.can_parse("some content", "song.cho") is True
        assert parser.can_parse("some content", "song.crd") is True
        assert parser.can_parse("some content", "song.chopro") is True

    def test_can_parse_by_content(self):
        """Should detect ChordPro by directives in content."""
        parser = ChordProParser()
        content = "{title: Test Song}\n[G]Lyrics here"
        assert parser.can_parse(content, "song.txt") is True

    def test_parse_basic_chordpro(self):
        """Should parse basic ChordPro content."""
        parser = ChordProParser()
        content = """{title: Test Song}
{artist: Test Artist}
{key: G}
{tempo: 120}

[G]This is a [D]test
"""
        result = parser.parse(content, "test.cho")

        assert result.success is True
        assert result.song_data is not None
        assert result.song_data.name == "Test Song"
        assert result.song_data.artist == "Test Artist"
        assert result.song_data.original_key == MusicalKey.G
        assert result.song_data.tempo_bpm == 120
        assert result.song_data.chordpro_chart == content

    def test_parse_extracts_lyrics(self):
        """Should extract plain lyrics without chords."""
        parser = ChordProParser()
        content = "{title: Test}\n[G]Hello [D]world"
        result = parser.parse(content, "test.cho")

        assert result.success is True
        assert result.song_data is not None
        assert "Hello world" in result.song_data.lyrics
        assert "[G]" not in result.song_data.lyrics

    def test_parse_sample_file(self):
        """Should parse sample ChordPro file."""
        sample_path = FIXTURES_DIR / "sample.cho"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "sample.cho")

        assert result.success is True
        assert result.detected_format == "chordpro"
        assert result.song_data is not None
        assert result.song_data.name == "Amazing Grace"
        assert result.song_data.artist == "John Newton"
        assert result.song_data.original_key == MusicalKey.G


class TestOpenLyricsParser:
    """Tests for OpenLyrics/OpenLP XML parser."""

    def test_can_parse_openlyrics(self):
        """Should detect OpenLyrics by namespace."""
        parser = OpenLyricsParser()
        content = '<?xml version="1.0"?><song xmlns="http://openlyrics.info/namespace/2009/song"></song>'
        assert parser.can_parse(content, "song.xml") is True

    def test_cannot_parse_non_xml(self):
        """Should not parse non-XML content."""
        parser = OpenLyricsParser()
        assert parser.can_parse("plain text", "song.txt") is False

    def test_parse_basic_openlyrics(self):
        """Should parse basic OpenLyrics XML."""
        parser = OpenLyricsParser()
        content = """<?xml version="1.0" encoding="UTF-8"?>
<song xmlns="http://openlyrics.info/namespace/2009/song">
  <properties>
    <titles><title>Test OpenLyrics</title></titles>
    <authors><author>Test Author</author></authors>
    <key>D</key>
    <tempo>100</tempo>
  </properties>
  <lyrics>
    <verse name="v1">
      <lines>Test lyrics here</lines>
    </verse>
  </lyrics>
</song>"""
        result = parser.parse(content, "test.xml")

        assert result.success is True
        assert result.song_data is not None
        assert result.song_data.name == "Test OpenLyrics"
        assert result.song_data.artist == "Test Author"
        assert result.song_data.original_key == MusicalKey.D
        assert result.song_data.tempo_bpm == 100

    def test_parse_sample_file(self):
        """Should parse sample OpenLyrics file."""
        sample_path = FIXTURES_DIR / "sample_openlyrics.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "sample_openlyrics.xml")

        assert result.success is True
        assert result.detected_format == "openlyrics"
        assert result.song_data is not None
        assert result.song_data.name == "Test Song OpenLyrics"
        assert result.song_data.original_key == MusicalKey.D


class TestOpenSongParser:
    """Tests for OpenSong XML parser."""

    def test_can_parse_opensong(self):
        """Should detect OpenSong by structure."""
        parser = OpenSongParser()
        content = "<song><title>Test</title><lyrics>test</lyrics></song>"
        assert parser.can_parse(content, "song.xml") is True

    def test_cannot_parse_openlyrics(self):
        """Should not parse OpenLyrics (different format)."""
        parser = OpenSongParser()
        content = '<song xmlns="http://openlyrics.info/namespace/2009/song"></song>'
        assert parser.can_parse(content, "song.xml") is False

    def test_parse_basic_opensong(self):
        """Should parse basic OpenSong XML."""
        parser = OpenSongParser()
        content = """<?xml version="1.0"?>
<song>
  <title>Test OpenSong</title>
  <author>Test Author</author>
  <key>A</key>
  <tempo>110</tempo>
  <lyrics>
[V]
.A       D
Test lyrics here
  </lyrics>
</song>"""
        result = parser.parse(content, "test.xml")

        assert result.success is True
        assert result.song_data is not None
        assert result.song_data.name == "Test OpenSong"
        assert result.song_data.artist == "Test Author"
        assert result.song_data.original_key == MusicalKey.A
        assert result.song_data.tempo_bpm == 110

    def test_parse_sample_file(self):
        """Should parse sample OpenSong file."""
        sample_path = FIXTURES_DIR / "sample_opensong.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "sample_opensong.xml")

        assert result.success is True
        assert result.detected_format == "opensong"
        assert result.song_data is not None
        assert result.song_data.name == "Test Song OpenSong"
        assert result.song_data.original_key == MusicalKey.A


class TestPlainTextParser:
    """Tests for plain text heuristic parser."""

    def test_can_parse_always_true(self):
        """Plain text parser is fallback - always returns True."""
        parser = PlainTextParser()
        assert parser.can_parse("anything", "any.file") is True

    def test_parse_with_metadata(self):
        """Should extract metadata from header lines."""
        parser = PlainTextParser()
        content = """Title: Test Plain Text
Artist: Test Artist
Key: E

E       A
Test lyrics here
"""
        result = parser.parse(content, "test.txt")

        assert result.success is True
        assert result.song_data is not None
        assert result.song_data.name == "Test Plain Text"
        assert result.song_data.artist == "Test Artist"
        assert result.song_data.original_key == MusicalKey.E

    def test_parse_chord_over_lyrics(self):
        """Should convert chord-over-lyrics to ChordPro."""
        parser = PlainTextParser()
        content = """Test Song

G       D       G
This is the lyrics
"""
        result = parser.parse(content, "test.txt")

        assert result.success is True
        assert result.song_data is not None
        # Should have ChordPro chart with inline chords
        assert result.song_data.chordpro_chart is not None
        assert "[G]" in result.song_data.chordpro_chart

    def test_parse_sample_file(self):
        """Should parse sample plain text file."""
        sample_path = FIXTURES_DIR / "sample.txt"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "sample.txt")

        assert result.success is True
        assert result.detected_format == "plaintext"
        assert result.song_data is not None
        assert result.song_data.name == "Test Song Plain Text"
        assert result.song_data.original_key == MusicalKey.E


class TestFormatDetection:
    """Tests for automatic format detection."""

    def test_detect_chordpro(self):
        """Should detect ChordPro format."""
        content = b"{title: Test}\n[G]Lyrics"
        result = detect_and_parse(content, "song.txt")
        assert result.detected_format == "chordpro"

    def test_detect_openlyrics(self):
        """Should detect OpenLyrics format."""
        content = b'<?xml version="1.0"?><song xmlns="http://openlyrics.info/namespace/2009/song"><properties><titles><title>Test</title></titles></properties><lyrics></lyrics></song>'
        result = detect_and_parse(content, "song.xml")
        assert result.detected_format == "openlyrics"

    def test_detect_opensong(self):
        """Should detect OpenSong format."""
        content = b"<song><title>Test</title><lyrics>text</lyrics></song>"
        result = detect_and_parse(content, "song.xml")
        assert result.detected_format == "opensong"

    def test_fallback_to_plaintext(self):
        """Should fall back to plain text for unrecognized content."""
        content = b"Just some plain text\nWith multiple lines"
        result = detect_and_parse(content, "song.txt")
        assert result.detected_format == "plaintext"

    def test_handles_utf8_encoding(self):
        """Should handle UTF-8 encoded content."""
        content = "{title: Canción Española}\n[G]Corazón".encode("utf-8")
        result = detect_and_parse(content, "song.cho")
        assert result.success is True
        assert result.song_data.name == "Canción Española"

    def test_handles_latin1_encoding(self):
        """Should handle Latin-1 encoded content."""
        content = "{title: Canción}\n[G]Test".encode("latin-1")
        result = detect_and_parse(content, "song.cho")
        assert result.success is True


class TestKeyNormalization:
    """Tests for musical key normalization."""

    @pytest.mark.parametrize(
        "key_str,expected",
        [
            ("G", MusicalKey.G),
            ("D", MusicalKey.D),
            ("A", MusicalKey.A),
            ("E", MusicalKey.E),
            ("B", MusicalKey.B),
            ("F#", MusicalKey.F_SHARP),
            ("C#", MusicalKey.C_SHARP),
            ("F", MusicalKey.F),
            ("Bb", MusicalKey.B_FLAT),
            ("Eb", MusicalKey.E_FLAT),
            ("Ab", MusicalKey.A_FLAT),
            ("Db", MusicalKey.D_FLAT),
            ("Gb", MusicalKey.G_FLAT),
            ("G major", MusicalKey.G),
            ("D maj", MusicalKey.D),
            ("Am", MusicalKey.A),  # Minor key treated as major for simplicity
        ],
    )
    def test_normalize_key(self, key_str: str, expected: MusicalKey):
        """Should normalize various key formats."""
        parser = ChordProParser()
        result = parser._normalize_key(key_str)
        assert result == expected

    def test_normalize_key_none(self):
        """Should return None for invalid key."""
        parser = ChordProParser()
        assert parser._normalize_key(None) is None
        assert parser._normalize_key("") is None
        assert parser._normalize_key("invalid") is None
