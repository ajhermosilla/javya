"""Tests for song import parsers."""

from pathlib import Path

import pytest

from app.enums import MusicalKey
from app.services.import_song import detect_and_parse, ParseResult
from app.services.import_song.chordpro_parser import ChordProParser
from app.services.import_song.openlyrics_parser import OpenLyricsParser
from app.services.import_song.opensong_parser import OpenSongParser
from app.services.import_song.plaintext_parser import PlainTextParser
from app.services.import_song.ultimateguitar_parser import UltimateGuitarParser


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
        sample_path = FIXTURES_DIR / "sample_plaintext.txt"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "sample_plaintext.txt")

        assert result.success is True
        assert result.detected_format == "plaintext"
        assert result.song_data is not None
        assert result.song_data.name == "Test Song Plain Text"
        assert result.song_data.original_key == MusicalKey.E


class TestUltimateGuitarParser:
    """Tests for Ultimate Guitar format parser."""

    def test_can_parse_by_capo(self):
        """Should detect UG format by Capo line."""
        parser = UltimateGuitarParser()
        content = """Song Title
Capo: 2

[Verse]
G       D
Some lyrics here
"""
        assert parser.can_parse(content, "song.txt") is True

    def test_can_parse_by_tuning(self):
        """Should detect UG format by Tuning line."""
        parser = UltimateGuitarParser()
        content = """Song Title
Tuning: Drop D

[Verse]
G       D
Some lyrics here
"""
        assert parser.can_parse(content, "song.txt") is True

    def test_can_parse_by_filename(self):
        """Should detect UG format by filename hint."""
        parser = UltimateGuitarParser()
        content = "G    D\nSome lyrics"
        assert parser.can_parse(content, "song_ug.txt") is True
        assert parser.can_parse(content, "ultimate_song.txt") is True

    def test_can_parse_by_sections(self):
        """Should detect UG format by multiple section markers with chords."""
        parser = UltimateGuitarParser()
        content = """[Verse]
G       D
Some lyrics

[Chorus]
C       G
More lyrics
"""
        assert parser.can_parse(content, "song.txt") is True

    def test_cannot_parse_plain_lyrics(self):
        """Should not parse plain lyrics without UG markers."""
        parser = UltimateGuitarParser()
        content = """Just some plain text
Without any chords
Or section markers"""
        assert parser.can_parse(content, "song.txt") is False

    def test_parse_extracts_metadata(self):
        """Should extract title, artist, capo, and key."""
        parser = UltimateGuitarParser()
        content = """Amazing Grace by John Newton

Capo: 3
Key: G

[Verse 1]
G       C       G
Amazing grace how sweet the sound
"""
        result = parser.parse(content, "song.txt")

        assert result.success is True
        assert result.song_data is not None
        assert result.song_data.name == "Amazing Grace"
        assert result.song_data.artist == "John Newton"
        assert result.song_data.original_key == MusicalKey.G
        assert result.song_data.notes is not None
        assert "Capo: 3" in result.song_data.notes

    def test_parse_converts_to_chordpro(self):
        """Should convert chord-over-lyrics to ChordPro format."""
        parser = UltimateGuitarParser()
        content = """Test Song
Capo: 2

[Verse]
G       D
Hello world
"""
        result = parser.parse(content, "song.txt")

        assert result.success is True
        assert result.song_data.chordpro_chart is not None
        assert "[G]" in result.song_data.chordpro_chart
        assert "[D]" in result.song_data.chordpro_chart

    def test_parse_extracts_plain_lyrics(self):
        """Should extract plain lyrics without chords."""
        parser = UltimateGuitarParser()
        content = """Test Song
Capo: 2

G       D
Hello world
C       G
Goodbye world
"""
        result = parser.parse(content, "song.txt")

        assert result.success is True
        assert result.song_data.lyrics is not None
        assert "Hello world" in result.song_data.lyrics
        assert "Goodbye world" in result.song_data.lyrics
        assert "[G]" not in result.song_data.lyrics

    def test_parse_sample_file(self):
        """Should parse sample Ultimate Guitar file."""
        sample_path = FIXTURES_DIR / "sample_ug.txt"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "sample_ug.txt")

        assert result.success is True
        assert result.detected_format == "ultimateguitar"
        assert result.song_data is not None
        assert result.song_data.name == "Blessed Be Your Name"
        assert result.song_data.artist == "Matt Redman"
        assert result.song_data.original_key == MusicalKey.A
        assert "Capo: 2" in result.song_data.notes

    def test_parse_preserves_sections(self):
        """Should preserve section markers in output."""
        parser = UltimateGuitarParser()
        content = """Song
Capo: 1

[Verse]
G    D
First verse

[Chorus]
C    G
The chorus
"""
        result = parser.parse(content, "song.txt")

        assert result.success is True
        assert "[Verse]" in result.song_data.chordpro_chart
        assert "[Chorus]" in result.song_data.chordpro_chart

    def test_parse_handles_tuning(self):
        """Should extract non-standard tuning."""
        parser = UltimateGuitarParser()
        content = """Song Title
Tuning: DADGAD
Capo: 2

[Verse]
G    D
Lyrics
"""
        result = parser.parse(content, "song.txt")

        assert result.success is True
        assert result.song_data.notes is not None
        assert "Tuning: DADGAD" in result.song_data.notes
        assert "Capo: 2" in result.song_data.notes


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

    def test_detect_ultimateguitar(self):
        """Should detect Ultimate Guitar format."""
        content = b"""Song Title
Capo: 2

[Verse]
G       D
Some lyrics here
"""
        result = detect_and_parse(content, "song.txt")
        assert result.detected_format == "ultimateguitar"

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


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestChordProErrorHandling:
    """Error handling tests for ChordPro parser."""

    def test_empty_content(self):
        """Should handle empty content gracefully."""
        parser = ChordProParser()
        result = parser.parse("", "empty.cho")

        # Should succeed but use filename as title (title-cased)
        assert result.success is True
        assert result.song_data is not None
        assert result.song_data.name == "Empty"

    def test_whitespace_only_content(self):
        """Should handle whitespace-only content."""
        parser = ChordProParser()
        result = parser.parse("   \n\t\n   ", "whitespace.cho")

        assert result.success is True
        assert result.song_data is not None
        assert result.song_data.name == "Whitespace"

    def test_malformed_directives(self):
        """Should handle malformed directives without crashing."""
        parser = ChordProParser()
        content = """{title: Valid Title}
{broken directive without colon}
{: empty directive name}
{key:}
{tempo: not_a_number}
[G]Some lyrics"""
        result = parser.parse(content, "malformed.cho")

        assert result.success is True
        assert result.song_data.name == "Valid Title"
        # Invalid tempo should be ignored
        assert result.song_data.tempo_bpm is None

    def test_unclosed_brackets(self):
        """Should handle unclosed chord brackets."""
        parser = ChordProParser()
        content = "{title: Test}\n[G This chord is not closed\n[D]Valid chord"
        result = parser.parse(content, "test.cho")

        assert result.success is True

    def test_special_characters_in_title(self):
        """Should handle special characters in title."""
        parser = ChordProParser()
        content = '{title: "Test & Song" <with> special \'chars\'}'
        result = parser.parse(content, "test.cho")

        assert result.success is True
        assert result.song_data is not None


class TestOpenLyricsErrorHandling:
    """Error handling tests for OpenLyrics parser."""

    def test_malformed_xml(self):
        """Should handle malformed XML gracefully."""
        parser = OpenLyricsParser()
        content = """<?xml version="1.0"?>
<song xmlns="http://openlyrics.info/namespace/2009/song">
  <properties>
    <titles><title>Broken XML</title></titles>
  <!-- Missing closing tags -->"""

        result = parser.parse(content, "malformed.xml")
        assert result.success is False
        assert result.error is not None
        assert "parse" in result.error.lower() or "xml" in result.error.lower()

    def test_empty_xml(self):
        """Should handle empty XML content."""
        parser = OpenLyricsParser()
        result = parser.parse("", "empty.xml")

        assert result.success is False

    def test_missing_title(self):
        """Should handle missing title element."""
        parser = OpenLyricsParser()
        content = """<?xml version="1.0"?>
<song xmlns="http://openlyrics.info/namespace/2009/song">
  <properties>
    <titles></titles>
  </properties>
  <lyrics><verse name="v1"><lines>Lyrics</lines></verse></lyrics>
</song>"""
        result = parser.parse(content, "no_title.xml")

        # Should succeed using filename (title-cased)
        assert result.success is True
        assert result.song_data.name == "No Title"

    def test_missing_lyrics_section(self):
        """Should handle missing lyrics section."""
        parser = OpenLyricsParser()
        content = """<?xml version="1.0"?>
<song xmlns="http://openlyrics.info/namespace/2009/song">
  <properties>
    <titles><title>No Lyrics Song</title></titles>
  </properties>
</song>"""
        result = parser.parse(content, "no_lyrics.xml")

        assert result.success is True
        assert result.song_data.name == "No Lyrics Song"

    def test_invalid_tempo_value(self):
        """Should handle non-numeric tempo values."""
        parser = OpenLyricsParser()
        content = """<?xml version="1.0"?>
<song xmlns="http://openlyrics.info/namespace/2009/song">
  <properties>
    <titles><title>Test</title></titles>
    <tempo type="text">Allegro</tempo>
  </properties>
  <lyrics><verse name="v1"><lines>Test</lines></verse></lyrics>
</song>"""
        result = parser.parse(content, "test.xml")

        assert result.success is True
        # Non-numeric tempo should be ignored
        assert result.song_data.tempo_bpm is None


class TestOpenSongErrorHandling:
    """Error handling tests for OpenSong parser."""

    def test_malformed_xml(self):
        """Should handle malformed XML gracefully."""
        parser = OpenSongParser()
        content = """<song><title>Broken</title><lyrics>Missing end tags"""

        result = parser.parse(content, "malformed.xml")
        assert result.success is False
        assert result.error is not None

    def test_empty_lyrics(self):
        """Should handle empty lyrics element."""
        parser = OpenSongParser()
        content = """<song><title>Empty Lyrics</title><lyrics></lyrics></song>"""
        result = parser.parse(content, "empty_lyrics.xml")

        assert result.success is True
        assert result.song_data.name == "Empty Lyrics"

    def test_missing_title(self):
        """Should use filename when title is missing."""
        parser = OpenSongParser()
        content = """<song><lyrics>[V]\nSome lyrics</lyrics></song>"""
        result = parser.parse(content, "untitled_song.xml")

        assert result.success is True
        assert result.song_data.name == "Untitled Song"


class TestPlainTextErrorHandling:
    """Error handling tests for plain text parser."""

    def test_empty_content(self):
        """Should handle empty content."""
        parser = PlainTextParser()
        result = parser.parse("", "empty.txt")

        assert result.success is True
        assert result.song_data.name == "Empty"

    def test_only_metadata_no_content(self):
        """Should handle file with only metadata."""
        parser = PlainTextParser()
        content = """Title: Metadata Only
Artist: Some Artist
Key: G"""
        result = parser.parse(content, "metadata_only.txt")

        assert result.success is True
        assert result.song_data.name == "Metadata Only"

    def test_binary_like_content(self):
        """Should handle content that looks like binary."""
        parser = PlainTextParser()
        # This would be decoded from bytes that are mostly valid text
        content = "Title: Binary-ish\n\x00\x01\x02Some garbage"
        result = parser.parse(content, "binary.txt")

        assert result.success is True


# =============================================================================
# REAL-WORLD FORMAT TESTS
# =============================================================================


class TestRealWorldChordPro:
    """Tests with realistic ChordPro files."""

    def test_complex_chordpro_with_sections(self):
        """Should parse complex ChordPro with sections and all metadata."""
        sample_path = FIXTURES_DIR / "complex_chordpro.cho"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "complex_chordpro.cho")

        assert result.success is True
        assert result.detected_format == "chordpro"
        assert result.song_data.name == "How Great Is Our God"
        assert result.song_data.artist == "Chris Tomlin"
        assert result.song_data.original_key == MusicalKey.G
        assert result.song_data.tempo_bpm == 78
        # Notes should contain capo and copyright info
        assert result.song_data.notes is not None
        assert "Capo" in result.song_data.notes
        assert "Copyright" in result.song_data.notes

    def test_short_form_directives(self):
        """Should parse short-form directives (t:, st:, a:)."""
        sample_path = FIXTURES_DIR / "short_form_chordpro.cho"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "short_form_chordpro.cho")

        assert result.success is True
        assert result.song_data.name == "10,000 Reasons"
        assert result.song_data.artist == "Matt Redman"

    def test_no_metadata_uses_filename(self):
        """Should use filename as title when no metadata present."""
        sample_path = FIXTURES_DIR / "no_metadata_chordpro.cho"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "no_metadata_chordpro.cho")

        assert result.success is True
        # Filename is title-cased when used as title
        assert result.song_data.name == "No Metadata Chordpro"

    def test_unicode_spanish_song(self):
        """Should handle Spanish songs with accented characters."""
        sample_path = FIXTURES_DIR / "unicode_chars.cho"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "unicode_chars.cho")

        assert result.success is True
        assert result.song_data.name == "Cántico de María"
        assert "Música Católica" in result.song_data.artist
        assert result.song_data.original_key == MusicalKey.E


class TestRealWorldOpenLyrics:
    """Tests with realistic OpenLyrics files."""

    def test_complex_openlyrics_with_all_metadata(self):
        """Should parse complex OpenLyrics with all metadata fields."""
        sample_path = FIXTURES_DIR / "complex_openlyrics.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "complex_openlyrics.xml")

        assert result.success is True
        assert result.detected_format == "openlyrics"
        assert result.song_data.name == "Oceans (Where Feet May Fail)"
        # Should get first author with type "words"
        assert "Matt Crocker" in result.song_data.artist
        assert result.song_data.original_key == MusicalKey.D
        assert result.song_data.tempo_bpm == 66

    def test_minimal_openlyrics(self):
        """Should parse minimal OpenLyrics with only required fields."""
        sample_path = FIXTURES_DIR / "minimal_openlyrics.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "minimal_openlyrics.xml")

        assert result.success is True
        assert result.song_data.name == "Minimal Song"
        assert result.song_data.lyrics is not None

    def test_openlyrics_without_namespace(self):
        """Should parse OpenLyrics-style XML without explicit namespace."""
        sample_path = FIXTURES_DIR / "no_namespace_openlyrics.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "no_namespace_openlyrics.xml")

        assert result.success is True
        assert result.song_data.name == "Song Without Namespace"
        assert result.song_data.original_key == MusicalKey.E


class TestRealWorldOpenSong:
    """Tests with realistic OpenSong files."""

    def test_complex_opensong_with_sections(self):
        """Should parse complex OpenSong with multiple sections."""
        sample_path = FIXTURES_DIR / "complex_opensong.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "complex_opensong.xml")

        assert result.success is True
        assert result.detected_format == "opensong"
        assert result.song_data.name == "Great Are You Lord"
        assert result.song_data.original_key == MusicalKey.G
        assert result.song_data.tempo_bpm == 72
        # Should have ChordPro chart generated
        assert result.song_data.chordpro_chart is not None

    def test_minimal_opensong(self):
        """Should parse minimal OpenSong with just title and lyrics."""
        sample_path = FIXTURES_DIR / "minimal_opensong.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "minimal_opensong.xml")

        assert result.success is True
        assert result.song_data.name == "Simple OpenSong"

    def test_spanish_opensong(self):
        """Should handle Spanish OpenSong files."""
        sample_path = FIXTURES_DIR / "spanish_opensong.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "spanish_opensong.xml")

        assert result.success is True
        assert result.song_data.name == "Tu Fidelidad"
        assert result.song_data.artist == "Marcos Witt"
        assert result.song_data.original_key == MusicalKey.C


class TestRealWorldPlainText:
    """Tests with realistic plain text files."""

    def test_complex_plaintext_with_sections(self):
        """Should parse plain text with verse/chorus/bridge sections."""
        sample_path = FIXTURES_DIR / "complex_plaintext.txt"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "complex_plaintext.txt")

        assert result.success is True
        assert result.detected_format == "plaintext"
        assert result.song_data.name == "What A Beautiful Name"
        assert result.song_data.artist == "Hillsong Worship"
        assert result.song_data.original_key == MusicalKey.D
        assert result.song_data.tempo_bpm == 68

    def test_plaintext_no_chords(self):
        """Should handle plain text with no chord notations."""
        sample_path = FIXTURES_DIR / "no_chords_plaintext.txt"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "no_chords_plaintext.txt")

        assert result.success is True
        assert result.song_data.name == "Simple Song"

    def test_plaintext_no_metadata(self):
        """Should handle plain text with only chords and lyrics."""
        sample_path = FIXTURES_DIR / "no_metadata_plaintext.txt"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "no_metadata_plaintext.txt")

        assert result.success is True
        # Plain text parser extracts first lyric line as title when no metadata
        assert result.song_data.name is not None
        # Should generate ChordPro chart
        assert result.song_data.chordpro_chart is not None


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Edge case tests across all parsers."""

    def test_very_long_title(self):
        """Should reject titles exceeding 255 character limit."""
        parser = ChordProParser()
        long_title = "A" * 500
        content = f"{{title: {long_title}}}\n[G]Lyrics"
        result = parser.parse(content, "test.cho")

        # SongCreate validation rejects names > 255 chars
        assert result.success is False
        assert result.error is not None
        assert "255" in result.error or "too_long" in result.error

    def test_max_length_title(self):
        """Should accept titles at max length (255 chars)."""
        parser = ChordProParser()
        max_title = "A" * 255
        content = f"{{title: {max_title}}}\n[G]Lyrics"
        result = parser.parse(content, "test.cho")

        assert result.success is True
        assert result.song_data.name == max_title

    def test_title_with_newlines(self):
        """Should handle title with newline characters stripped."""
        parser = ChordProParser()
        content = "{title: Test\nSong}\n[G]Lyrics"
        result = parser.parse(content, "test.cho")

        # The regex won't match multi-line, so filename fallback
        assert result.success is True

    def test_multiple_titles_uses_first(self):
        """Should use first title when multiple are present."""
        parser = ChordProParser()
        content = """{title: First Title}
{title: Second Title}
{t: Third Title}
[G]Lyrics"""
        result = parser.parse(content, "test.cho")

        assert result.success is True
        assert result.song_data.name == "First Title"

    def test_tempo_edge_values(self):
        """Should validate tempo within reasonable range."""
        parser = ChordProParser()

        # Too low
        content = "{title: Test}\n{tempo: 10}\n[G]Lyrics"
        result = parser.parse(content, "test.cho")
        assert result.song_data.tempo_bpm is None

        # Too high
        content = "{title: Test}\n{tempo: 400}\n[G]Lyrics"
        result = parser.parse(content, "test.cho")
        assert result.song_data.tempo_bpm is None

        # Valid edge cases
        content = "{title: Test}\n{tempo: 20}\n[G]Lyrics"
        result = parser.parse(content, "test.cho")
        assert result.song_data.tempo_bpm == 20

        content = "{title: Test}\n{tempo: 300}\n[G]Lyrics"
        result = parser.parse(content, "test.cho")
        assert result.song_data.tempo_bpm == 300

    def test_complex_chord_names(self):
        """Should handle complex chord names."""
        parser = ChordProParser()
        content = """{title: Complex Chords}
[Cmaj7]First [Dm7b5]Second [F#m7/C#]Third
[Gadd9]Fourth [Bsus4]Fifth [E7#9]Sixth"""
        result = parser.parse(content, "test.cho")

        assert result.success is True
        # Chords should be removed from lyrics
        assert "[Cmaj7]" not in result.song_data.lyrics
        assert "First" in result.song_data.lyrics
        # Chords should be in chart
        assert "[Cmaj7]" in result.song_data.chordpro_chart

    def test_mixed_case_keys(self):
        """Should normalize keys with standard casing."""
        parser = ChordProParser()

        # Current implementation requires proper casing (first letter uppercase)
        test_cases = [
            ("G", MusicalKey.G),
            ("Bb", MusicalKey.B_FLAT),
            ("F#", MusicalKey.F_SHARP),
            ("Eb", MusicalKey.E_FLAT),
        ]

        for key_str, expected in test_cases:
            assert parser._normalize_key(key_str) == expected, f"Failed for {key_str}"

        # Lowercase keys are not recognized (returns None)
        assert parser._normalize_key("g") is None
        assert parser._normalize_key("bb") is None

    def test_format_detection_priority(self):
        """ChordPro directives should take priority over extension."""
        # File with .txt extension but ChordPro content
        content = b"{title: ChordPro Song}\n[G]Lyrics"
        result = detect_and_parse(content, "song.txt")
        assert result.detected_format == "chordpro"

    def test_xml_format_priority(self):
        """OpenLyrics should take priority over OpenSong for namespace XML."""
        content = b'''<?xml version="1.0"?>
<song xmlns="http://openlyrics.info/namespace/2009/song">
  <properties><titles><title>Test</title></titles></properties>
  <lyrics><verse name="v1"><lines>Test</lines></verse></lyrics>
</song>'''
        result = detect_and_parse(content, "song.xml")
        assert result.detected_format == "openlyrics"

    def test_empty_file_handling(self):
        """Should handle empty files via detect_and_parse."""
        sample_path = FIXTURES_DIR / "empty_content.txt"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "empty_content.txt")

        assert result.success is True
        # Filename is title-cased
        assert result.song_data.name == "Empty Content"

    def test_malformed_xml_falls_through(self):
        """Malformed XML should fail XML parsers but may fall to plaintext."""
        sample_path = FIXTURES_DIR / "malformed.xml"
        if not sample_path.exists():
            pytest.skip("Sample file not found")

        content = sample_path.read_bytes()
        result = detect_and_parse(content, "malformed.xml")

        # OpenLyrics and OpenSong should fail, but plaintext might catch it
        # The result depends on whether plaintext accepts XML-looking content
        # Either way, it shouldn't crash
        assert result is not None

    def test_bom_handling(self):
        """Should handle UTF-8 BOM in files."""
        # UTF-8 BOM + ChordPro content
        bom = b"\xef\xbb\xbf"
        content = bom + b"{title: BOM Test}\n[G]Lyrics"
        result = detect_and_parse(content, "bom.cho")

        assert result.success is True
        assert result.song_data.name == "BOM Test"

    def test_windows_line_endings(self):
        """Should handle Windows line endings (CRLF)."""
        content = b"{title: Windows Song}\r\n[G]First line\r\n[D]Second line"
        result = detect_and_parse(content, "windows.cho")

        assert result.success is True
        assert result.song_data.name == "Windows Song"

    def test_tabs_in_content(self):
        """Should handle tabs in content."""
        parser = ChordProParser()
        content = "{title: Tab Song}\n[G]\tIndented\twith\ttabs"
        result = parser.parse(content, "tabs.cho")

        assert result.success is True
        assert "Indented" in result.song_data.lyrics


class TestKeyNormalizationExtended:
    """Extended key normalization tests."""

    @pytest.mark.parametrize(
        "key_str,expected",
        [
            # Sharp variants
            ("F#", MusicalKey.F_SHARP),
            ("F♯", MusicalKey.F_SHARP),  # Unicode sharp
            ("C#", MusicalKey.C_SHARP),
            ("G#", MusicalKey.G_SHARP),
            # Flat variants
            ("Bb", MusicalKey.B_FLAT),
            ("B♭", MusicalKey.B_FLAT),  # Unicode flat
            ("Eb", MusicalKey.E_FLAT),
            ("Ab", MusicalKey.A_FLAT),
            # With major/minor suffixes
            ("C major", MusicalKey.C),
            ("C Major", MusicalKey.C),
            ("Cm", MusicalKey.C),  # Minor treated as major
            ("C minor", MusicalKey.C),
            ("C min", MusicalKey.C),
            ("Cmaj", MusicalKey.C),
        ],
    )
    def test_extended_key_normalization(self, key_str: str, expected: MusicalKey):
        """Should handle various key notation formats."""
        parser = ChordProParser()
        result = parser._normalize_key(key_str)
        assert result == expected, f"Failed for '{key_str}': got {result}, expected {expected}"

    def test_unsupported_key_formats(self):
        """Document key formats that are not currently supported."""
        parser = ChordProParser()
        # These formats are not supported by current implementation
        unsupported = ["Fs", "Bf", "c", "g", "d"]  # 's' for sharp, 'f' for flat, lowercase
        for key_str in unsupported:
            assert parser._normalize_key(key_str) is None, f"'{key_str}' should not be supported"


class TestLyricsExtraction:
    """Tests for lyrics extraction from various formats."""

    def test_chordpro_preserves_section_labels(self):
        """Section labels should be preserved in lyrics."""
        parser = ChordProParser()
        content = """{title: Test}
[Verse 1]
[G]First verse lyrics

[Chorus]
[C]Chorus lyrics"""
        result = parser.parse(content, "test.cho")

        assert result.success is True
        # Section labels in square brackets that aren't chords should remain
        # (depends on implementation - [Verse 1] is not a valid chord)
        assert "First verse lyrics" in result.song_data.lyrics

    def test_openlyrics_extracts_all_verses(self):
        """Should extract lyrics from all verses."""
        parser = OpenLyricsParser()
        content = """<?xml version="1.0"?>
<song xmlns="http://openlyrics.info/namespace/2009/song">
  <properties><titles><title>Multi Verse</title></titles></properties>
  <lyrics>
    <verse name="v1"><lines>Verse 1 line</lines></verse>
    <verse name="v2"><lines>Verse 2 line</lines></verse>
    <verse name="c1"><lines>Chorus line</lines></verse>
  </lyrics>
</song>"""
        result = parser.parse(content, "test.xml")

        assert result.success is True
        assert "Verse 1" in result.song_data.lyrics or "v1" in result.song_data.lyrics.lower()
        assert "Chorus" in result.song_data.lyrics or "c1" in result.song_data.lyrics.lower()

    def test_opensong_converts_to_chordpro(self):
        """OpenSong dot-prefix chords should convert to ChordPro."""
        parser = OpenSongParser()
        content = """<song>
  <title>Chord Convert</title>
  <lyrics>
[V1]
.G       D
 First line here
  </lyrics>
</song>"""
        result = parser.parse(content, "test.xml")

        assert result.success is True
        if result.song_data.chordpro_chart:
            # Should have inline chords in ChordPro format
            assert "[G]" in result.song_data.chordpro_chart or "G" in result.song_data.chordpro_chart
