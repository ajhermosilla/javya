package dev.cronova.javya.util

/**
 * Chord transposition utilities with proper enharmonic spelling.
 *
 * Based on the Circle of Fifths:
 * - Sharp keys (clockwise): C, G, D, A, E, B, F#, C#
 * - Flat keys (counter-clockwise): F, Bb, Eb, Ab, Db, Gb
 *
 * The output spelling is determined by the target key:
 * - Transposing to F outputs Bb (not A#)
 * - Transposing to D outputs F# (not Gb)
 */
object TransposeUtil {

    // Notes in chromatic order using sharps
    val SHARP_NOTES = listOf("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

    // Notes in chromatic order using flats
    val FLAT_NOTES = listOf("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")

    // Keys that use sharp notation (Circle of Fifths clockwise)
    val SHARP_KEYS = listOf("C", "G", "D", "A", "E", "B", "F#", "C#")

    // Keys that use flat notation (Circle of Fifths counter-clockwise)
    val FLAT_KEYS = listOf("F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb")

    // "Easy" keys for guitar - open chord shapes
    val EASY_GUITAR_KEYS = listOf("G", "C", "D", "A", "E")

    // Display-friendly key order for UI dropdowns
    val DISPLAY_KEYS = listOf(
        "C", "G", "D", "A", "E", "B", "F#",  // Sharp keys
        "F", "Bb", "Eb", "Ab", "Db", "Gb"    // Flat keys
    )

    // Map enharmonic equivalents to semitone index
    private val NOTE_TO_SEMITONE = mapOf(
        "C" to 0, "B#" to 0,
        "C#" to 1, "Db" to 1,
        "D" to 2,
        "D#" to 3, "Eb" to 3,
        "E" to 4, "Fb" to 4,
        "F" to 5, "E#" to 5,
        "F#" to 6, "Gb" to 6,
        "G" to 7,
        "G#" to 8, "Ab" to 8,
        "A" to 9,
        "A#" to 10, "Bb" to 10,
        "B" to 11, "Cb" to 11
    )

    // Chord pattern regex for validation
    private val CHORD_PATTERN = Regex("^[A-Ga-g][#b]?(m|maj|min|dim|aug|sus|add|[0-9])*(/[A-Ga-g][#b]?)?$")

    // Root note pattern regex for parsing
    private val ROOT_PATTERN = Regex("^([A-Ga-g])([#b]?)(.*)$")

    // Bass note pattern regex for validation
    private val BASS_PATTERN = Regex("^[A-Ga-g][#b]?$")

    /**
     * Normalize key name to standard format (capitalize first letter).
     */
    fun normalizeKeyName(key: String): String {
        if (key.isEmpty()) return key
        return key[0].uppercaseChar() + key.substring(1).lowercase()
    }

    /**
     * Check if a key uses sharp notation.
     */
    fun usesSharps(key: String): Boolean {
        val normalized = normalizeKeyName(key)
        return normalized in SHARP_KEYS
    }

    /**
     * Get semitone index (0-11) for a note.
     * Handles both sharp and flat notation.
     *
     * @throws IllegalArgumentException if note is invalid
     */
    fun noteToSemitone(note: String): Int {
        val normalized = normalizeKeyName(note)
        return NOTE_TO_SEMITONE[normalized]
            ?: throw IllegalArgumentException("Invalid note: $note")
    }

    /**
     * Convert semitone index to note name using appropriate spelling.
     */
    fun semitoneToNote(semitone: Int, useSharps: Boolean): String {
        val index = ((semitone % 12) + 12) % 12
        return if (useSharps) SHARP_NOTES[index] else FLAT_NOTES[index]
    }

    /**
     * Calculate semitone interval between two keys.
     */
    fun calculateInterval(fromKey: String, toKey: String): Int {
        val fromSemitone = noteToSemitone(fromKey)
        val toSemitone = noteToSemitone(toKey)
        return ((toSemitone - fromSemitone) + 12) % 12
    }

    /**
     * Transpose a single note by a number of semitones.
     */
    fun transposeNote(note: String, semitones: Int, useSharps: Boolean): String {
        val currentSemitone = noteToSemitone(note)
        return semitoneToNote(currentSemitone + semitones, useSharps)
    }

    /**
     * Parsed chord components.
     */
    data class ChordComponents(
        val root: String,
        val quality: String,
        val bass: String?
    )

    /**
     * Parse a chord into its components.
     * Examples:
     *   "G" -> ChordComponents("G", "", null)
     *   "Am7" -> ChordComponents("A", "m7", null)
     *   "F#m/C#" -> ChordComponents("F#", "m", "C#")
     *
     * @return null if chord is invalid
     */
    fun parseChord(chord: String): ChordComponents? {
        // Handle slash chords (bass note)
        val slashIndex = chord.lastIndexOf('/')
        val mainChord: String
        val bass: String?

        if (slashIndex > 0) {
            mainChord = chord.substring(0, slashIndex)
            bass = chord.substring(slashIndex + 1)
            // Validate bass note
            if (!BASS_PATTERN.matches(bass)) {
                return null
            }
        } else {
            mainChord = chord
            bass = null
        }

        // Parse root note and quality
        val match = ROOT_PATTERN.find(mainChord) ?: return null
        val (rootLetter, accidental, quality) = match.destructured
        val root = rootLetter.uppercase() + accidental

        return ChordComponents(root, quality, bass)
    }

    /**
     * Transpose a single chord by a number of semitones.
     */
    fun transposeChord(chord: String, semitones: Int, useSharps: Boolean): String {
        val components = parseChord(chord) ?: return chord // Invalid chord, return as-is

        val newRoot = transposeNote(components.root, semitones, useSharps)
        var result = newRoot + components.quality

        components.bass?.let { bass ->
            val newBass = transposeNote(bass, semitones, useSharps)
            result += "/$newBass"
        }

        return result
    }

    /**
     * Check if a bracketed string is a chord (vs section header like [Verse]).
     */
    fun isChord(content: String): Boolean {
        return CHORD_PATTERN.matches(content)
    }

    /**
     * Transpose all chords in a ChordPro string.
     * Section headers like [Verse 1] are preserved unchanged.
     */
    fun transposeChordPro(
        chordpro: String,
        fromKey: String,
        toKey: String
    ): String {
        if (chordpro.isEmpty() || fromKey.isEmpty() || fromKey == toKey) {
            return chordpro
        }

        val semitones = calculateInterval(fromKey, toKey)
        val useSharps = usesSharps(toKey)

        // Replace all bracketed content that is a chord
        return Regex("\\[([^\\]]+)]").replace(chordpro) { matchResult ->
            val content = matchResult.groupValues[1]
            if (isChord(content)) {
                "[${transposeChord(content, semitones, useSharps)}]"
            } else {
                // Section header, return unchanged
                matchResult.value
            }
        }
    }

    /**
     * Capo suggestion with played key.
     */
    data class CapoSuggestion(
        val capo: Int,
        val playedKey: String
    )

    /**
     * Calculate what key the guitarist would play if using a capo.
     * If target is F and capo is on fret 1, play E shapes.
     */
    fun getPlayedKey(targetKey: String, capoFret: Int): String {
        val targetSemitone = noteToSemitone(targetKey)
        // Playing with capo means the shapes are lower by capo semitones
        val playedSemitone = (targetSemitone - capoFret + 12) % 12
        // Return the played key using sharps (guitar convention)
        return semitoneToNote(playedSemitone, true)
    }

    /**
     * Suggest capo positions for a target key.
     * Returns positions where the played key is one of the easy guitar keys.
     */
    fun suggestCapo(targetKey: String): List<CapoSuggestion> {
        val suggestions = mutableListOf<CapoSuggestion>()

        // Check capo positions 1-7 (beyond 7 gets uncomfortable)
        for (capo in 1..7) {
            val playedKey = getPlayedKey(targetKey, capo)
            if (playedKey in EASY_GUITAR_KEYS) {
                suggestions.add(CapoSuggestion(capo, playedKey))
            }
        }

        // Sort by ease of played key (G > C > D > A > E) then by lower capo
        suggestions.sortWith(compareBy(
            { EASY_GUITAR_KEYS.indexOf(it.playedKey) },
            { it.capo }
        ))

        return suggestions
    }

    /**
     * Check if a key is considered "difficult" for guitar (needs barre chords).
     */
    fun isDifficultKey(key: String): Boolean {
        return try {
            val semitone = noteToSemitone(key)
            val normalizedKey = semitoneToNote(semitone, true)
            normalizedKey !in EASY_GUITAR_KEYS
        } catch (e: IllegalArgumentException) {
            false
        }
    }
}
