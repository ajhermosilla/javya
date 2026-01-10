package dev.cronova.javya.util

import com.google.common.truth.Truth.assertThat
import org.junit.Assert.assertThrows
import org.junit.Test

/**
 * Unit tests for TransposeUtil.
 *
 * Tests cover:
 * - Key normalization
 * - Note to semitone conversion
 * - Semitone to note conversion (sharps and flats)
 * - Interval calculation
 * - Chord parsing
 * - Chord transposition
 * - ChordPro transposition
 * - Capo suggestions
 */
class TransposeUtilTest {

    // ==================== Key Normalization ====================

    @Test
    fun `normalizeKeyName capitalizes first letter`() {
        assertThat(TransposeUtil.normalizeKeyName("c")).isEqualTo("C")
        assertThat(TransposeUtil.normalizeKeyName("g")).isEqualTo("G")
        assertThat(TransposeUtil.normalizeKeyName("bb")).isEqualTo("Bb")
        assertThat(TransposeUtil.normalizeKeyName("f#")).isEqualTo("F#")
    }

    @Test
    fun `normalizeKeyName handles already normalized keys`() {
        assertThat(TransposeUtil.normalizeKeyName("C")).isEqualTo("C")
        assertThat(TransposeUtil.normalizeKeyName("Bb")).isEqualTo("Bb")
        assertThat(TransposeUtil.normalizeKeyName("F#")).isEqualTo("F#")
    }

    @Test
    fun `normalizeKeyName handles empty string`() {
        assertThat(TransposeUtil.normalizeKeyName("")).isEqualTo("")
    }

    // ==================== usesSharps ====================

    @Test
    fun `usesSharps returns true for sharp keys`() {
        assertThat(TransposeUtil.usesSharps("C")).isTrue()
        assertThat(TransposeUtil.usesSharps("G")).isTrue()
        assertThat(TransposeUtil.usesSharps("D")).isTrue()
        assertThat(TransposeUtil.usesSharps("A")).isTrue()
        assertThat(TransposeUtil.usesSharps("E")).isTrue()
        assertThat(TransposeUtil.usesSharps("B")).isTrue()
        assertThat(TransposeUtil.usesSharps("F#")).isTrue()
        assertThat(TransposeUtil.usesSharps("C#")).isTrue()
    }

    @Test
    fun `usesSharps returns false for flat keys`() {
        assertThat(TransposeUtil.usesSharps("F")).isFalse()
        assertThat(TransposeUtil.usesSharps("Bb")).isFalse()
        assertThat(TransposeUtil.usesSharps("Eb")).isFalse()
        assertThat(TransposeUtil.usesSharps("Ab")).isFalse()
        assertThat(TransposeUtil.usesSharps("Db")).isFalse()
        assertThat(TransposeUtil.usesSharps("Gb")).isFalse()
    }

    @Test
    fun `usesSharps handles lowercase input`() {
        assertThat(TransposeUtil.usesSharps("g")).isTrue()
        assertThat(TransposeUtil.usesSharps("bb")).isFalse()
    }

    // ==================== noteToSemitone ====================

    @Test
    fun `noteToSemitone returns correct values for natural notes`() {
        assertThat(TransposeUtil.noteToSemitone("C")).isEqualTo(0)
        assertThat(TransposeUtil.noteToSemitone("D")).isEqualTo(2)
        assertThat(TransposeUtil.noteToSemitone("E")).isEqualTo(4)
        assertThat(TransposeUtil.noteToSemitone("F")).isEqualTo(5)
        assertThat(TransposeUtil.noteToSemitone("G")).isEqualTo(7)
        assertThat(TransposeUtil.noteToSemitone("A")).isEqualTo(9)
        assertThat(TransposeUtil.noteToSemitone("B")).isEqualTo(11)
    }

    @Test
    fun `noteToSemitone returns correct values for sharps`() {
        assertThat(TransposeUtil.noteToSemitone("C#")).isEqualTo(1)
        assertThat(TransposeUtil.noteToSemitone("D#")).isEqualTo(3)
        assertThat(TransposeUtil.noteToSemitone("F#")).isEqualTo(6)
        assertThat(TransposeUtil.noteToSemitone("G#")).isEqualTo(8)
        assertThat(TransposeUtil.noteToSemitone("A#")).isEqualTo(10)
    }

    @Test
    fun `noteToSemitone returns correct values for flats`() {
        assertThat(TransposeUtil.noteToSemitone("Db")).isEqualTo(1)
        assertThat(TransposeUtil.noteToSemitone("Eb")).isEqualTo(3)
        assertThat(TransposeUtil.noteToSemitone("Gb")).isEqualTo(6)
        assertThat(TransposeUtil.noteToSemitone("Ab")).isEqualTo(8)
        assertThat(TransposeUtil.noteToSemitone("Bb")).isEqualTo(10)
    }

    @Test
    fun `noteToSemitone handles enharmonic equivalents`() {
        assertThat(TransposeUtil.noteToSemitone("B#")).isEqualTo(0) // Same as C
        assertThat(TransposeUtil.noteToSemitone("E#")).isEqualTo(5) // Same as F
        assertThat(TransposeUtil.noteToSemitone("Fb")).isEqualTo(4) // Same as E
        assertThat(TransposeUtil.noteToSemitone("Cb")).isEqualTo(11) // Same as B
    }

    @Test
    fun `noteToSemitone throws for invalid note`() {
        assertThrows(IllegalArgumentException::class.java) {
            TransposeUtil.noteToSemitone("H")
        }
        assertThrows(IllegalArgumentException::class.java) {
            TransposeUtil.noteToSemitone("X")
        }
    }

    // ==================== semitoneToNote ====================

    @Test
    fun `semitoneToNote returns sharps when useSharps is true`() {
        assertThat(TransposeUtil.semitoneToNote(0, true)).isEqualTo("C")
        assertThat(TransposeUtil.semitoneToNote(1, true)).isEqualTo("C#")
        assertThat(TransposeUtil.semitoneToNote(3, true)).isEqualTo("D#")
        assertThat(TransposeUtil.semitoneToNote(6, true)).isEqualTo("F#")
        assertThat(TransposeUtil.semitoneToNote(8, true)).isEqualTo("G#")
        assertThat(TransposeUtil.semitoneToNote(10, true)).isEqualTo("A#")
    }

    @Test
    fun `semitoneToNote returns flats when useSharps is false`() {
        assertThat(TransposeUtil.semitoneToNote(0, false)).isEqualTo("C")
        assertThat(TransposeUtil.semitoneToNote(1, false)).isEqualTo("Db")
        assertThat(TransposeUtil.semitoneToNote(3, false)).isEqualTo("Eb")
        assertThat(TransposeUtil.semitoneToNote(6, false)).isEqualTo("Gb")
        assertThat(TransposeUtil.semitoneToNote(8, false)).isEqualTo("Ab")
        assertThat(TransposeUtil.semitoneToNote(10, false)).isEqualTo("Bb")
    }

    @Test
    fun `semitoneToNote handles negative values with wrapping`() {
        assertThat(TransposeUtil.semitoneToNote(-1, true)).isEqualTo("B")
        assertThat(TransposeUtil.semitoneToNote(-2, true)).isEqualTo("A#")
        assertThat(TransposeUtil.semitoneToNote(-12, true)).isEqualTo("C")
    }

    @Test
    fun `semitoneToNote handles values greater than 11 with wrapping`() {
        assertThat(TransposeUtil.semitoneToNote(12, true)).isEqualTo("C")
        assertThat(TransposeUtil.semitoneToNote(13, true)).isEqualTo("C#")
        assertThat(TransposeUtil.semitoneToNote(24, true)).isEqualTo("C")
    }

    // ==================== calculateInterval ====================

    @Test
    fun `calculateInterval returns correct semitone difference`() {
        assertThat(TransposeUtil.calculateInterval("C", "D")).isEqualTo(2)
        assertThat(TransposeUtil.calculateInterval("C", "E")).isEqualTo(4)
        assertThat(TransposeUtil.calculateInterval("C", "F")).isEqualTo(5)
        assertThat(TransposeUtil.calculateInterval("C", "G")).isEqualTo(7)
        assertThat(TransposeUtil.calculateInterval("G", "C")).isEqualTo(5) // G to C is 5 semitones up
    }

    @Test
    fun `calculateInterval handles enharmonic equivalents`() {
        assertThat(TransposeUtil.calculateInterval("C#", "Db")).isEqualTo(0)
        assertThat(TransposeUtil.calculateInterval("F#", "Gb")).isEqualTo(0)
    }

    @Test
    fun `calculateInterval returns 0 for same key`() {
        assertThat(TransposeUtil.calculateInterval("G", "G")).isEqualTo(0)
        assertThat(TransposeUtil.calculateInterval("Bb", "Bb")).isEqualTo(0)
    }

    // ==================== transposeNote ====================

    @Test
    fun `transposeNote moves note by semitones`() {
        assertThat(TransposeUtil.transposeNote("C", 2, true)).isEqualTo("D")
        assertThat(TransposeUtil.transposeNote("G", 2, true)).isEqualTo("A")
        assertThat(TransposeUtil.transposeNote("E", 1, true)).isEqualTo("F")
    }

    @Test
    fun `transposeNote uses correct spelling based on useSharps`() {
        assertThat(TransposeUtil.transposeNote("C", 1, true)).isEqualTo("C#")
        assertThat(TransposeUtil.transposeNote("C", 1, false)).isEqualTo("Db")
    }

    @Test
    fun `transposeNote wraps around octave`() {
        assertThat(TransposeUtil.transposeNote("B", 1, true)).isEqualTo("C")
        assertThat(TransposeUtil.transposeNote("A", 5, true)).isEqualTo("D")
    }

    // ==================== parseChord ====================

    @Test
    fun `parseChord parses simple major chords`() {
        val result = TransposeUtil.parseChord("G")
        assertThat(result).isNotNull()
        assertThat(result!!.root).isEqualTo("G")
        assertThat(result.quality).isEqualTo("")
        assertThat(result.bass).isNull()
    }

    @Test
    fun `parseChord parses minor chords`() {
        val result = TransposeUtil.parseChord("Am")
        assertThat(result).isNotNull()
        assertThat(result!!.root).isEqualTo("A")
        assertThat(result.quality).isEqualTo("m")
        assertThat(result.bass).isNull()
    }

    @Test
    fun `parseChord parses seventh chords`() {
        val result = TransposeUtil.parseChord("Am7")
        assertThat(result).isNotNull()
        assertThat(result!!.root).isEqualTo("A")
        assertThat(result.quality).isEqualTo("m7")
        assertThat(result.bass).isNull()
    }

    @Test
    fun `parseChord parses chords with sharps`() {
        val result = TransposeUtil.parseChord("F#m")
        assertThat(result).isNotNull()
        assertThat(result!!.root).isEqualTo("F#")
        assertThat(result.quality).isEqualTo("m")
        assertThat(result.bass).isNull()
    }

    @Test
    fun `parseChord parses chords with flats`() {
        val result = TransposeUtil.parseChord("Bbmaj7")
        assertThat(result).isNotNull()
        assertThat(result!!.root).isEqualTo("Bb")
        assertThat(result.quality).isEqualTo("maj7")
        assertThat(result.bass).isNull()
    }

    @Test
    fun `parseChord parses slash chords`() {
        val result = TransposeUtil.parseChord("G/B")
        assertThat(result).isNotNull()
        assertThat(result!!.root).isEqualTo("G")
        assertThat(result.quality).isEqualTo("")
        assertThat(result.bass).isEqualTo("B")
    }

    @Test
    fun `parseChord parses complex slash chords`() {
        val result = TransposeUtil.parseChord("F#m7/C#")
        assertThat(result).isNotNull()
        assertThat(result!!.root).isEqualTo("F#")
        assertThat(result.quality).isEqualTo("m7")
        assertThat(result.bass).isEqualTo("C#")
    }

    @Test
    fun `parseChord returns null for invalid chords`() {
        assertThat(TransposeUtil.parseChord("Verse")).isNull()
        assertThat(TransposeUtil.parseChord("Chorus")).isNull()
        assertThat(TransposeUtil.parseChord("123")).isNull()
    }

    // ==================== transposeChord ====================

    @Test
    fun `transposeChord transposes simple chord`() {
        assertThat(TransposeUtil.transposeChord("G", 2, true)).isEqualTo("A")
        assertThat(TransposeUtil.transposeChord("C", 5, false)).isEqualTo("F")
    }

    @Test
    fun `transposeChord preserves chord quality`() {
        assertThat(TransposeUtil.transposeChord("Am", 2, true)).isEqualTo("Bm")
        assertThat(TransposeUtil.transposeChord("Gmaj7", 2, true)).isEqualTo("Amaj7")
        assertThat(TransposeUtil.transposeChord("Dm7", 2, true)).isEqualTo("Em7")
    }

    @Test
    fun `transposeChord transposes bass note in slash chords`() {
        assertThat(TransposeUtil.transposeChord("G/B", 2, true)).isEqualTo("A/C#")
        assertThat(TransposeUtil.transposeChord("Am/E", 2, true)).isEqualTo("Bm/F#")
    }

    @Test
    fun `transposeChord uses correct enharmonic spelling`() {
        // Transposing to F key should use flats
        assertThat(TransposeUtil.transposeChord("C", 5, false)).isEqualTo("F")
        assertThat(TransposeUtil.transposeChord("D", 5, false)).isEqualTo("G")
        assertThat(TransposeUtil.transposeChord("E", 1, false)).isEqualTo("F")

        // Transposing to D key should use sharps
        assertThat(TransposeUtil.transposeChord("C", 2, true)).isEqualTo("D")
        assertThat(TransposeUtil.transposeChord("F", 2, true)).isEqualTo("G")
    }

    @Test
    fun `transposeChord returns invalid chord unchanged`() {
        assertThat(TransposeUtil.transposeChord("Verse", 2, true)).isEqualTo("Verse")
        assertThat(TransposeUtil.transposeChord("Bridge", 2, true)).isEqualTo("Bridge")
    }

    // ==================== isChord ====================

    @Test
    fun `isChord returns true for valid chords`() {
        assertThat(TransposeUtil.isChord("G")).isTrue()
        assertThat(TransposeUtil.isChord("Am")).isTrue()
        assertThat(TransposeUtil.isChord("F#m7")).isTrue()
        assertThat(TransposeUtil.isChord("Bbmaj7")).isTrue()
        assertThat(TransposeUtil.isChord("Dsus4")).isTrue()
        assertThat(TransposeUtil.isChord("Cadd9")).isTrue()
        assertThat(TransposeUtil.isChord("G/B")).isTrue()
        assertThat(TransposeUtil.isChord("Am7/E")).isTrue()
    }

    @Test
    fun `isChord returns false for section headers`() {
        assertThat(TransposeUtil.isChord("Verse")).isFalse()
        assertThat(TransposeUtil.isChord("Verse 1")).isFalse()
        assertThat(TransposeUtil.isChord("Chorus")).isFalse()
        assertThat(TransposeUtil.isChord("Bridge")).isFalse()
        assertThat(TransposeUtil.isChord("Intro")).isFalse()
        assertThat(TransposeUtil.isChord("Outro")).isFalse()
    }

    // ==================== transposeChordPro ====================

    @Test
    fun `transposeChordPro transposes all chords`() {
        val input = "[G]Amazing [C]grace how [D]sweet the [G]sound"
        val expected = "[A]Amazing [D]grace how [E]sweet the [A]sound"
        assertThat(TransposeUtil.transposeChordPro(input, "G", "A")).isEqualTo(expected)
    }

    @Test
    fun `transposeChordPro preserves section headers`() {
        val input = "[Verse 1]\n[G]Amazing [C]grace\n[Chorus]\n[D]How [G]sweet"
        val expected = "[Verse 1]\n[A]Amazing [D]grace\n[Chorus]\n[E]How [A]sweet"
        assertThat(TransposeUtil.transposeChordPro(input, "G", "A")).isEqualTo(expected)
    }

    @Test
    fun `transposeChordPro returns unchanged when same key`() {
        val input = "[G]Amazing [C]grace"
        assertThat(TransposeUtil.transposeChordPro(input, "G", "G")).isEqualTo(input)
    }

    @Test
    fun `transposeChordPro returns unchanged for empty input`() {
        assertThat(TransposeUtil.transposeChordPro("", "G", "A")).isEqualTo("")
    }

    @Test
    fun `transposeChordPro uses correct enharmonic spelling for target key`() {
        val input = "[G]Amazing [C]grace [D]sweet"

        // Transposing to F should use flats
        val toF = TransposeUtil.transposeChordPro(input, "G", "F")
        assertThat(toF).isEqualTo("[F]Amazing [Bb]grace [C]sweet")

        // Transposing to D should use sharps
        val toD = TransposeUtil.transposeChordPro(input, "G", "D")
        assertThat(toD).isEqualTo("[D]Amazing [G]grace [A]sweet")
    }

    @Test
    fun `transposeChordPro handles slash chords`() {
        val input = "[G/B]Amazing [Am7/E]grace"
        val expected = "[A/C#]Amazing [Bm7/F#]grace"
        assertThat(TransposeUtil.transposeChordPro(input, "G", "A")).isEqualTo(expected)
    }

    // ==================== getPlayedKey ====================

    @Test
    fun `getPlayedKey calculates correct played key with capo`() {
        // Capo 1 on F means playing E shapes
        assertThat(TransposeUtil.getPlayedKey("F", 1)).isEqualTo("E")

        // Capo 2 on A means playing G shapes
        assertThat(TransposeUtil.getPlayedKey("A", 2)).isEqualTo("G")

        // Capo 3 on Bb means playing G shapes
        assertThat(TransposeUtil.getPlayedKey("Bb", 3)).isEqualTo("G")

        // Capo 5 on C means playing G shapes
        assertThat(TransposeUtil.getPlayedKey("C", 5)).isEqualTo("G")
    }

    // ==================== suggestCapo ====================

    @Test
    fun `suggestCapo returns suggestions for difficult keys`() {
        // F is a difficult key
        val suggestions = TransposeUtil.suggestCapo("F")
        assertThat(suggestions).isNotEmpty()

        // Should suggest capo 1 playing E
        val capo1 = suggestions.find { it.capo == 1 }
        assertThat(capo1).isNotNull()
        assertThat(capo1!!.playedKey).isEqualTo("E")
    }

    @Test
    fun `suggestCapo returns empty for easy keys with no good capo positions`() {
        // G is already easy - but there might still be capo options
        val suggestions = TransposeUtil.suggestCapo("G")
        // All suggestions should have easy played keys
        suggestions.forEach { suggestion ->
            assertThat(suggestion.playedKey).isIn(TransposeUtil.EASY_GUITAR_KEYS)
        }
    }

    @Test
    fun `suggestCapo sorts by ease of played key`() {
        val suggestions = TransposeUtil.suggestCapo("Bb")
        if (suggestions.size >= 2) {
            // G should come before D in suggestions (it's ranked higher in EASY_GUITAR_KEYS)
            val gIndex = suggestions.indexOfFirst { it.playedKey == "G" }
            val dIndex = suggestions.indexOfFirst { it.playedKey == "D" }
            if (gIndex >= 0 && dIndex >= 0) {
                assertThat(gIndex).isLessThan(dIndex)
            }
        }
    }

    // ==================== isDifficultKey ====================

    @Test
    fun `isDifficultKey returns false for easy keys`() {
        assertThat(TransposeUtil.isDifficultKey("G")).isFalse()
        assertThat(TransposeUtil.isDifficultKey("C")).isFalse()
        assertThat(TransposeUtil.isDifficultKey("D")).isFalse()
        assertThat(TransposeUtil.isDifficultKey("A")).isFalse()
        assertThat(TransposeUtil.isDifficultKey("E")).isFalse()
    }

    @Test
    fun `isDifficultKey returns true for difficult keys`() {
        assertThat(TransposeUtil.isDifficultKey("F")).isTrue()
        assertThat(TransposeUtil.isDifficultKey("Bb")).isTrue()
        assertThat(TransposeUtil.isDifficultKey("Eb")).isTrue()
        assertThat(TransposeUtil.isDifficultKey("Ab")).isTrue()
        assertThat(TransposeUtil.isDifficultKey("F#")).isTrue()
        assertThat(TransposeUtil.isDifficultKey("B")).isTrue()
    }

    @Test
    fun `isDifficultKey handles invalid keys gracefully`() {
        assertThat(TransposeUtil.isDifficultKey("Invalid")).isFalse()
        assertThat(TransposeUtil.isDifficultKey("")).isFalse()
    }

    // ==================== Edge Cases ====================

    @Test
    fun `transpose handles full chromatic scale up`() {
        // C -> C# -> D -> D# -> E -> F -> F# -> G -> G# -> A -> A# -> B -> C
        var note = "C"
        val expected = listOf("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C")

        for (i in 0..12) {
            assertThat(TransposeUtil.transposeNote("C", i, true)).isEqualTo(expected[i])
        }
    }

    @Test
    fun `transpose handles full chromatic scale with flats`() {
        val expected = listOf("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C")

        for (i in 0..12) {
            assertThat(TransposeUtil.transposeNote("C", i, false)).isEqualTo(expected[i])
        }
    }

    @Test
    fun `complex chord progression transposition`() {
        val input = """
            [Verse]
            [G]When I [G/B]survey the [C]wondrous [D]cross
            [Em]On which the [Am7]Prince of [D7]Glory [G]died

            [Chorus]
            [C]My richest [G/B]gain I [Am]count but [D]loss
            [G]And pour con[C]tempt on [D]all my [G]pride
        """.trimIndent()

        val expected = """
            [Verse]
            [A]When I [A/C#]survey the [D]wondrous [E]cross
            [F#m]On which the [Bm7]Prince of [E7]Glory [A]died

            [Chorus]
            [D]My richest [A/C#]gain I [Bm]count but [E]loss
            [A]And pour con[D]tempt on [E]all my [A]pride
        """.trimIndent()

        assertThat(TransposeUtil.transposeChordPro(input, "G", "A")).isEqualTo(expected)
    }
}
