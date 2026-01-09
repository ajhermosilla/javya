"""Tests for key detection algorithm."""

import pytest

from app.enums import MusicalKey
from app.services.import_song.key_detector import (
    KeyConfidence,
    KeyDetectionResult,
    KeyDetector,
)


class TestKeyDetector:
    """Tests for the KeyDetector class."""

    @pytest.fixture
    def detector(self) -> KeyDetector:
        """Create a KeyDetector instance."""
        return KeyDetector()

    def test_detect_g_major_simple(self, detector: KeyDetector):
        """Should detect G major from G-C-D progression."""
        chords = ["G", "C", "D", "G"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.G

    def test_detect_g_major_with_extensions(self, detector: KeyDetector):
        """Should detect G major from chords with extensions."""
        chords = ["G", "Em7", "C", "D7", "G", "Cadd9", "D"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.G

    def test_detect_c_major(self, detector: KeyDetector):
        """Should detect C major from C-F-G progression."""
        chords = ["C", "F", "G", "C", "Am", "F", "G", "C"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.C

    def test_detect_d_major(self, detector: KeyDetector):
        """Should detect D major from D-G-A progression."""
        chords = ["D", "G", "A", "D", "Bm", "G", "A", "D"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.D

    def test_detect_a_major(self, detector: KeyDetector):
        """Should detect A major from A-D-E progression."""
        chords = ["A", "D", "E", "A"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.A

    def test_detect_e_major(self, detector: KeyDetector):
        """Should detect E major from E-A-B progression."""
        chords = ["E", "A", "B", "E", "A", "B", "E"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.E

    def test_detect_f_major(self, detector: KeyDetector):
        """Should detect F major from F-Bb-C progression."""
        chords = ["F", "Bb", "C", "F", "Dm", "Bb", "C", "F"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.F

    def test_detect_key_with_slash_chords(self, detector: KeyDetector):
        """Should detect key ignoring bass notes in slash chords."""
        chords = ["G", "G/B", "C", "D/F#", "G"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.G

    def test_detect_key_with_minor_chords(self, detector: KeyDetector):
        """Should detect key when minor chords are present."""
        chords = ["G", "Em", "C", "D", "G", "Em", "Am", "D"]
        result = detector.detect_key(chords)

        # G major has Em and Am as vi and ii chords
        assert result.detected_key == MusicalKey.G

    def test_detect_key_lowercase_chords(self, detector: KeyDetector):
        """Should handle lowercase chord names."""
        chords = ["g", "c", "d", "g"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.G

    def test_detect_key_with_unicode_accidentals(self, detector: KeyDetector):
        """Should handle unicode sharp and flat symbols."""
        chords = ["F♯", "B", "C♯", "F♯"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.F_SHARP

    def test_detect_key_with_flat_notation(self, detector: KeyDetector):
        """Should handle flat notation."""
        chords = ["Bb", "Eb", "F", "Bb"]
        result = detector.detect_key(chords)

        assert result.detected_key == MusicalKey.B_FLAT

    def test_empty_chord_list(self, detector: KeyDetector):
        """Should return None for empty chord list."""
        result = detector.detect_key([])

        assert result.detected_key is None
        assert result.confidence == KeyConfidence.LOW
        assert result.confidence_score == 0.0

    def test_single_chord(self, detector: KeyDetector):
        """Should detect key from single repeated chord."""
        chords = ["G"]
        result = detector.detect_key(chords)

        # G is most likely the tonic
        assert result.detected_key == MusicalKey.G

    def test_low_confidence_chromatic(self, detector: KeyDetector):
        """Should report low confidence for chromatic/ambiguous progressions."""
        # All 12 notes equally - very ambiguous
        chords = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        result = detector.detect_key(chords)

        assert result.confidence == KeyConfidence.LOW

    def test_invalid_chord_names(self, detector: KeyDetector):
        """Should handle invalid chord names gracefully."""
        chords = ["X", "???", "", "G", "C", "D"]
        result = detector.detect_key(chords)

        # Should still detect G from valid chords
        assert result.detected_key == MusicalKey.G

    def test_complex_chord_names(self, detector: KeyDetector):
        """Should extract root from complex chord names."""
        chords = [
            "Cmaj7",
            "Dm7",
            "Em7b5",
            "Fmaj7#11",
            "G7sus4",
            "Am7add9",
            "Bdim7",
        ]
        result = detector.detect_key(chords)

        # This is a C major scale chord set
        assert result.detected_key == MusicalKey.C


class TestExtractRoot:
    """Tests for the _extract_root method."""

    @pytest.fixture
    def detector(self) -> KeyDetector:
        """Create a KeyDetector instance."""
        return KeyDetector()

    def test_simple_major(self, detector: KeyDetector):
        """Should extract root from simple major chord."""
        assert detector._extract_root("C") == "C"
        assert detector._extract_root("G") == "G"
        assert detector._extract_root("D") == "D"

    def test_minor(self, detector: KeyDetector):
        """Should extract root from minor chord."""
        assert detector._extract_root("Am") == "A"
        assert detector._extract_root("Em") == "E"
        assert detector._extract_root("Dm") == "D"

    def test_seventh(self, detector: KeyDetector):
        """Should extract root from seventh chord."""
        assert detector._extract_root("G7") == "G"
        assert detector._extract_root("Cmaj7") == "C"
        assert detector._extract_root("Dm7") == "D"

    def test_sharp(self, detector: KeyDetector):
        """Should extract root from sharp chord."""
        assert detector._extract_root("F#") == "F#"
        assert detector._extract_root("C#m") == "C#"
        assert detector._extract_root("G#7") == "G#"

    def test_flat(self, detector: KeyDetector):
        """Should extract root from flat chord."""
        assert detector._extract_root("Bb") == "Bb"
        assert detector._extract_root("Ebm") == "Eb"
        assert detector._extract_root("Ab7") == "Ab"

    def test_unicode_sharp(self, detector: KeyDetector):
        """Should handle unicode sharp symbol."""
        assert detector._extract_root("F♯") == "F#"
        assert detector._extract_root("C♯m7") == "C#"

    def test_unicode_flat(self, detector: KeyDetector):
        """Should handle unicode flat symbol."""
        assert detector._extract_root("B♭") == "Bb"
        assert detector._extract_root("E♭maj7") == "Eb"

    def test_slash_chord(self, detector: KeyDetector):
        """Should extract root (not bass) from slash chord."""
        assert detector._extract_root("G/B") == "G"
        assert detector._extract_root("D/F#") == "D"
        assert detector._extract_root("C/E") == "C"

    def test_lowercase(self, detector: KeyDetector):
        """Should handle lowercase chord names."""
        assert detector._extract_root("g") == "G"
        assert detector._extract_root("am") == "A"
        assert detector._extract_root("f#") == "F#"

    def test_empty_string(self, detector: KeyDetector):
        """Should return None for empty string."""
        assert detector._extract_root("") is None

    def test_invalid_chord(self, detector: KeyDetector):
        """Should return None for invalid chord name."""
        assert detector._extract_root("X") is None
        assert detector._extract_root("???") is None
        assert detector._extract_root("123") is None
