"""Key detection from chord progressions.

Uses music theory principles based on the Circle of Fifths to analyze
chord progressions and detect the most likely musical key.
"""

import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum

from app.enums import MusicalKey


class KeyConfidence(str, Enum):
    """Confidence level for detected key."""

    HIGH = "high"  # >70% certainty, clear winner
    MEDIUM = "medium"  # 50-70% certainty
    LOW = "low"  # <50% certainty, multiple candidates


@dataclass
class KeyDetectionResult:
    """Result from key detection analysis."""

    detected_key: MusicalKey | None
    confidence: KeyConfidence
    confidence_score: float  # 0.0 to 1.0


class KeyDetector:
    """Detects musical key from chord progressions.

    Uses the Circle of Fifths and chord function analysis to determine
    the most likely key of a song based on its chord progression.
    """

    # Chromatic scale: note name -> semitone value (C=0)
    NOTE_TO_SEMITONE: dict[str, int] = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
    }

    # Semitone -> MusicalKey mapping (prefer sharps for sharp keys, flats for flat keys)
    SEMITONE_TO_KEY: dict[int, MusicalKey] = {
        0: MusicalKey.C,
        1: MusicalKey.C_SHARP,
        2: MusicalKey.D,
        3: MusicalKey.E_FLAT,
        4: MusicalKey.E,
        5: MusicalKey.F,
        6: MusicalKey.F_SHARP,
        7: MusicalKey.G,
        8: MusicalKey.A_FLAT,
        9: MusicalKey.A,
        10: MusicalKey.B_FLAT,
        11: MusicalKey.B,
    }

    # Major scale intervals (semitones from root): I, ii, iii, IV, V, vi, vii°
    # Index is scale degree (0=I, 1=ii, etc.), value is semitone offset
    MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]

    # Chord function weights for key detection
    # Higher weight = stronger indicator of key
    CHORD_WEIGHTS = {
        0: 3.0,  # I (tonic) - strongest indicator
        7: 2.5,  # V (dominant) - very strong
        5: 2.0,  # IV (subdominant) - strong
        9: 1.5,  # vi (relative minor)
        2: 1.0,  # ii
        4: 1.0,  # iii
        11: 0.5,  # vii° (leading tone)
    }

    # Chord root extraction pattern - matches note letter + optional accidental
    CHORD_ROOT_PATTERN = re.compile(r"^([A-Ga-g])([#b♯♭])?")

    def detect_key(self, chords: list[str]) -> KeyDetectionResult:
        """Detect the most likely key from a list of chord names.

        Args:
            chords: List of chord strings (e.g., ["G", "C", "D7", "Em"])

        Returns:
            KeyDetectionResult with detected key, confidence level, and score
        """
        if not chords:
            return KeyDetectionResult(
                detected_key=None,
                confidence=KeyConfidence.LOW,
                confidence_score=0.0,
            )

        # Extract root notes and count them
        root_semitones: list[int] = []
        for chord in chords:
            root = self._extract_root(chord)
            if root is not None:
                semitone = self.NOTE_TO_SEMITONE.get(root)
                if semitone is not None:
                    root_semitones.append(semitone)

        if not root_semitones:
            return KeyDetectionResult(
                detected_key=None,
                confidence=KeyConfidence.LOW,
                confidence_score=0.0,
            )

        # Count chord root frequencies
        root_counts = Counter(root_semitones)

        # Calculate score for each possible key (0-11 semitones)
        key_scores: dict[int, float] = {}
        for candidate_root in range(12):
            score = self._calculate_key_score(root_counts, candidate_root)
            key_scores[candidate_root] = score

        # Find top candidates
        sorted_keys = sorted(key_scores.items(), key=lambda x: x[1], reverse=True)
        best_key, best_score = sorted_keys[0]
        second_score = sorted_keys[1][1] if len(sorted_keys) > 1 else 0.0

        # Calculate confidence based on margin between best and second best
        if best_score > 0 and second_score >= 0:
            # Margin: how much better is the best compared to second best
            margin = (best_score - second_score) / best_score
            confidence_score = margin
        else:
            confidence_score = 0.0

        # Determine confidence level based on margin
        # A clear winner has a large margin over the second candidate
        if confidence_score >= 0.3:
            confidence = KeyConfidence.HIGH
        elif confidence_score >= 0.15:
            confidence = KeyConfidence.MEDIUM
        else:
            confidence = KeyConfidence.LOW

        detected_key = self.SEMITONE_TO_KEY.get(best_key)

        return KeyDetectionResult(
            detected_key=detected_key,
            confidence=confidence,
            confidence_score=confidence_score,
        )

    def _extract_root(self, chord: str) -> str | None:
        """Extract root note from chord string.

        Args:
            chord: Chord string like "Am7", "D/F#", "Cmaj7"

        Returns:
            Root note in standard format (e.g., "A", "D", "C") or None
        """
        if not chord:
            return None

        chord = chord.strip()
        match = self.CHORD_ROOT_PATTERN.match(chord)
        if not match:
            return None

        note = match.group(1).upper()
        accidental = match.group(2)

        if accidental:
            # Normalize accidentals
            if accidental in ("b", "♭"):
                note += "b"
            elif accidental in ("#", "♯"):
                note += "#"

        return note

    def _calculate_key_score(
        self, root_counts: Counter[int], candidate_key: int
    ) -> float:
        """Calculate how well the chord roots fit a candidate key.

        Args:
            root_counts: Counter of root note semitones
            candidate_key: Semitone value of candidate key root (0=C, 7=G, etc.)

        Returns:
            Score indicating how well chords fit this key (higher = better fit)
        """
        score = 0.0

        for root_semitone, count in root_counts.items():
            # Calculate interval from candidate key root
            interval = (root_semitone - candidate_key) % 12

            # Get weight for this interval (0 if not in scale)
            weight = self.CHORD_WEIGHTS.get(interval, -0.3)

            # Add weighted count to score
            score += weight * count

        return score
