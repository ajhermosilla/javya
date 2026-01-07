from enum import Enum


class MusicalKey(str, Enum):
    """Musical keys following the Circle of Fifths.

    Sharp keys (clockwise): C, G, D, A, E, B, F#, C#
    Flat keys (counter-clockwise): F, Bb, Eb, Ab, Db, Gb

    Note: Enharmonic equivalents (e.g., G# = Ab) are kept for backward
    compatibility, but flat notation is preferred for flat keys.
    """

    # Natural key
    C = "C"

    # Sharp keys (Circle of Fifths clockwise)
    G = "G"
    D = "D"
    A = "A"
    E = "E"
    B = "B"
    F_SHARP = "F#"
    C_SHARP = "C#"

    # Flat keys (Circle of Fifths counter-clockwise)
    F = "F"
    B_FLAT = "Bb"
    E_FLAT = "Eb"
    A_FLAT = "Ab"
    D_FLAT = "Db"
    G_FLAT = "Gb"

    # Enharmonic equivalents (kept for backward compatibility)
    # These are rarely used in practice but supported for existing data
    D_SHARP = "D#"  # = Eb
    G_SHARP = "G#"  # = Ab
    A_SHARP = "A#"  # = Bb
