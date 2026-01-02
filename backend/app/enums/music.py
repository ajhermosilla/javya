from enum import Enum


class Key(str, Enum):
    """Musical keys for songs."""

    C = "C"
    C_SHARP = "C#"
    D_FLAT = "Db"
    D = "D"
    D_SHARP = "D#"
    E_FLAT = "Eb"
    E = "E"
    F = "F"
    F_SHARP = "F#"
    G_FLAT = "Gb"
    G = "G"
    G_SHARP = "G#"
    A_FLAT = "Ab"
    A = "A"
    A_SHARP = "A#"
    B_FLAT = "Bb"
    B = "B"
    # Minor keys
    C_MINOR = "Cm"
    D_MINOR = "Dm"
    E_MINOR = "Em"
    F_MINOR = "Fm"
    G_MINOR = "Gm"
    A_MINOR = "Am"
    B_MINOR = "Bm"


class Mood(str, Enum):
    """Mood/energy level of a song for worship flow."""

    REFLECTIVE = "reflective"
    INTIMATE = "intimate"
    JOYFUL = "joyful"
    TRIUMPHANT = "triumphant"
    DECLARATIVE = "declarative"
    MEDITATIVE = "meditative"
    CELEBRATORY = "celebratory"


class Theme(str, Enum):
    """Thematic categories for songs."""

    PRAISE = "praise"
    WORSHIP = "worship"
    THANKSGIVING = "thanksgiving"
    ADORATION = "adoration"
    CONFESSION = "confession"
    SURRENDER = "surrender"
    FAITH = "faith"
    HOPE = "hope"
    LOVE = "love"
    GRACE = "grace"
    SALVATION = "salvation"
    HEALING = "healing"
    COMFORT = "comfort"
    WARFARE = "warfare"
    CHRISTMAS = "christmas"
    EASTER = "easter"
    COMMUNION = "communion"
