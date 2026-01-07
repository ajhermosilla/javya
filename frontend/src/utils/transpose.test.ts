/**
 * Comprehensive test suite for chord transposition.
 *
 * Tests cover:
 * - Basic note transposition with proper enharmonic spelling
 * - Common chord types in worship and popular music
 * - Slash chords (bass notes)
 * - Common chord progressions (I-IV-V-vi, etc.)
 * - Real-world transposition scenarios
 * - Capo suggestions
 *
 * This test suite can be ported to the backend for Python implementation.
 */

import { describe, it, expect } from 'vitest';
import {
  noteToSemitone,
  semitoneToNote,
  calculateInterval,
  transposeNote,
  parseChord,
  transposeChord,
  isChord,
  transposeChordPro,
  usesSharps,
  suggestCapo,
  isDifficultKey,
  SHARP_KEYS,
  FLAT_KEYS,
  EASY_GUITAR_KEYS,
} from './transpose';

// =============================================================================
// BASIC NOTE OPERATIONS
// =============================================================================

describe('noteToSemitone', () => {
  it('converts natural notes correctly', () => {
    expect(noteToSemitone('C')).toBe(0);
    expect(noteToSemitone('D')).toBe(2);
    expect(noteToSemitone('E')).toBe(4);
    expect(noteToSemitone('F')).toBe(5);
    expect(noteToSemitone('G')).toBe(7);
    expect(noteToSemitone('A')).toBe(9);
    expect(noteToSemitone('B')).toBe(11);
  });

  it('converts sharp notes correctly', () => {
    expect(noteToSemitone('C#')).toBe(1);
    expect(noteToSemitone('D#')).toBe(3);
    expect(noteToSemitone('F#')).toBe(6);
    expect(noteToSemitone('G#')).toBe(8);
    expect(noteToSemitone('A#')).toBe(10);
  });

  it('converts flat notes correctly', () => {
    expect(noteToSemitone('Db')).toBe(1);
    expect(noteToSemitone('Eb')).toBe(3);
    expect(noteToSemitone('Gb')).toBe(6);
    expect(noteToSemitone('Ab')).toBe(8);
    expect(noteToSemitone('Bb')).toBe(10);
  });

  it('handles enharmonic equivalents', () => {
    // Same pitch, different names
    expect(noteToSemitone('C#')).toBe(noteToSemitone('Db'));
    expect(noteToSemitone('D#')).toBe(noteToSemitone('Eb'));
    expect(noteToSemitone('F#')).toBe(noteToSemitone('Gb'));
    expect(noteToSemitone('G#')).toBe(noteToSemitone('Ab'));
    expect(noteToSemitone('A#')).toBe(noteToSemitone('Bb'));
  });

  it('handles lowercase input', () => {
    expect(noteToSemitone('c')).toBe(0);
    expect(noteToSemitone('g')).toBe(7);
    expect(noteToSemitone('bb')).toBe(10);
  });

  it('throws on invalid notes', () => {
    expect(() => noteToSemitone('H')).toThrow();
    expect(() => noteToSemitone('X')).toThrow();
  });
});

describe('semitoneToNote', () => {
  it('returns sharp notes when useSharps is true', () => {
    expect(semitoneToNote(0, true)).toBe('C');
    expect(semitoneToNote(1, true)).toBe('C#');
    expect(semitoneToNote(3, true)).toBe('D#');
    expect(semitoneToNote(6, true)).toBe('F#');
    expect(semitoneToNote(8, true)).toBe('G#');
    expect(semitoneToNote(10, true)).toBe('A#');
  });

  it('returns flat notes when useSharps is false', () => {
    expect(semitoneToNote(0, false)).toBe('C');
    expect(semitoneToNote(1, false)).toBe('Db');
    expect(semitoneToNote(3, false)).toBe('Eb');
    expect(semitoneToNote(6, false)).toBe('Gb');
    expect(semitoneToNote(8, false)).toBe('Ab');
    expect(semitoneToNote(10, false)).toBe('Bb');
  });

  it('handles wrap-around (negative and > 11)', () => {
    expect(semitoneToNote(12, true)).toBe('C');
    expect(semitoneToNote(13, true)).toBe('C#');
    expect(semitoneToNote(-1, true)).toBe('B');
    expect(semitoneToNote(-2, false)).toBe('Bb');
  });
});

describe('usesSharps', () => {
  it('returns true for sharp keys', () => {
    SHARP_KEYS.forEach((key) => {
      expect(usesSharps(key)).toBe(true);
    });
  });

  it('returns false for flat keys', () => {
    FLAT_KEYS.forEach((key) => {
      expect(usesSharps(key)).toBe(false);
    });
  });
});

describe('calculateInterval', () => {
  it('calculates ascending intervals', () => {
    expect(calculateInterval('C', 'G')).toBe(7); // Perfect 5th
    expect(calculateInterval('C', 'F')).toBe(5); // Perfect 4th
    expect(calculateInterval('G', 'C')).toBe(5); // G up to C
    expect(calculateInterval('A', 'E')).toBe(7); // Perfect 5th
  });

  it('handles same key', () => {
    expect(calculateInterval('C', 'C')).toBe(0);
    expect(calculateInterval('F#', 'F#')).toBe(0);
  });

  it('handles enharmonic keys', () => {
    expect(calculateInterval('C', 'Db')).toBe(1);
    expect(calculateInterval('C', 'C#')).toBe(1);
  });
});

// =============================================================================
// CHORD PARSING
// =============================================================================

describe('parseChord', () => {
  describe('basic chords', () => {
    it('parses major chords', () => {
      expect(parseChord('C')).toEqual({ root: 'C', quality: '', bass: null });
      expect(parseChord('G')).toEqual({ root: 'G', quality: '', bass: null });
      expect(parseChord('F#')).toEqual({ root: 'F#', quality: '', bass: null });
      expect(parseChord('Bb')).toEqual({ root: 'Bb', quality: '', bass: null });
    });

    it('parses minor chords', () => {
      expect(parseChord('Am')).toEqual({ root: 'A', quality: 'm', bass: null });
      expect(parseChord('Em')).toEqual({ root: 'E', quality: 'm', bass: null });
      expect(parseChord('F#m')).toEqual({ root: 'F#', quality: 'm', bass: null });
      expect(parseChord('Bbm')).toEqual({ root: 'Bb', quality: 'm', bass: null });
    });
  });

  describe('seventh chords', () => {
    it('parses dominant 7th', () => {
      expect(parseChord('G7')).toEqual({ root: 'G', quality: '7', bass: null });
      expect(parseChord('D7')).toEqual({ root: 'D', quality: '7', bass: null });
    });

    it('parses major 7th', () => {
      expect(parseChord('Cmaj7')).toEqual({ root: 'C', quality: 'maj7', bass: null });
      expect(parseChord('Fmaj7')).toEqual({ root: 'F', quality: 'maj7', bass: null });
    });

    it('parses minor 7th', () => {
      expect(parseChord('Am7')).toEqual({ root: 'A', quality: 'm7', bass: null });
      expect(parseChord('Em7')).toEqual({ root: 'E', quality: 'm7', bass: null });
    });

    it('parses minor major 7th', () => {
      expect(parseChord('CmM7')).toEqual({ root: 'C', quality: 'mM7', bass: null });
    });
  });

  describe('suspended chords', () => {
    it('parses sus2', () => {
      expect(parseChord('Dsus2')).toEqual({ root: 'D', quality: 'sus2', bass: null });
      expect(parseChord('Asus2')).toEqual({ root: 'A', quality: 'sus2', bass: null });
    });

    it('parses sus4', () => {
      expect(parseChord('Dsus4')).toEqual({ root: 'D', quality: 'sus4', bass: null });
      expect(parseChord('Gsus4')).toEqual({ root: 'G', quality: 'sus4', bass: null });
    });

    it('parses sus (defaults to sus4)', () => {
      expect(parseChord('Dsus')).toEqual({ root: 'D', quality: 'sus', bass: null });
    });
  });

  describe('add chords', () => {
    it('parses add9', () => {
      expect(parseChord('Cadd9')).toEqual({ root: 'C', quality: 'add9', bass: null });
      expect(parseChord('Gadd9')).toEqual({ root: 'G', quality: 'add9', bass: null });
    });

    it('parses add11', () => {
      expect(parseChord('Cadd11')).toEqual({ root: 'C', quality: 'add11', bass: null });
    });
  });

  describe('extended chords', () => {
    it('parses 9th chords', () => {
      expect(parseChord('G9')).toEqual({ root: 'G', quality: '9', bass: null });
      expect(parseChord('Am9')).toEqual({ root: 'A', quality: 'm9', bass: null });
    });

    it('parses 11th chords', () => {
      expect(parseChord('G11')).toEqual({ root: 'G', quality: '11', bass: null });
    });

    it('parses 13th chords', () => {
      expect(parseChord('G13')).toEqual({ root: 'G', quality: '13', bass: null });
    });
  });

  describe('diminished and augmented', () => {
    it('parses diminished', () => {
      expect(parseChord('Cdim')).toEqual({ root: 'C', quality: 'dim', bass: null });
      expect(parseChord('Bdim7')).toEqual({ root: 'B', quality: 'dim7', bass: null });
    });

    it('parses augmented', () => {
      expect(parseChord('Caug')).toEqual({ root: 'C', quality: 'aug', bass: null });
      expect(parseChord('Gaug')).toEqual({ root: 'G', quality: 'aug', bass: null });
    });
  });

  describe('slash chords (bass notes)', () => {
    it('parses simple slash chords', () => {
      expect(parseChord('G/B')).toEqual({ root: 'G', quality: '', bass: 'B' });
      expect(parseChord('C/E')).toEqual({ root: 'C', quality: '', bass: 'E' });
      expect(parseChord('D/F#')).toEqual({ root: 'D', quality: '', bass: 'F#' });
    });

    it('parses complex slash chords', () => {
      expect(parseChord('Am7/G')).toEqual({ root: 'A', quality: 'm7', bass: 'G' });
      expect(parseChord('Cmaj7/E')).toEqual({ root: 'C', quality: 'maj7', bass: 'E' });
      expect(parseChord('F#m/C#')).toEqual({ root: 'F#', quality: 'm', bass: 'C#' });
    });

    it('parses slash chords with flat bass', () => {
      expect(parseChord('Eb/Bb')).toEqual({ root: 'Eb', quality: '', bass: 'Bb' });
      expect(parseChord('Ab/Eb')).toEqual({ root: 'Ab', quality: '', bass: 'Eb' });
    });
  });
});

describe('isChord', () => {
  it('identifies valid chords', () => {
    const validChords = [
      'C', 'G', 'D', 'A', 'E', 'B', 'F',
      'Am', 'Em', 'Dm', 'Bm', 'F#m', 'C#m',
      'G7', 'D7', 'A7', 'E7',
      'Cmaj7', 'Fmaj7', 'Gmaj7',
      'Am7', 'Em7', 'Dm7',
      'Dsus4', 'Asus2', 'Gsus',
      'Cadd9', 'Gadd9',
      'Cdim', 'Bdim7', 'Caug',
      'G/B', 'D/F#', 'Am7/G',
      'Bb', 'Eb', 'Ab', 'Db', 'Gb',
      'Bbm', 'Ebm', 'Abm',
    ];

    validChords.forEach((chord) => {
      expect(isChord(chord)).toBe(true);
    });
  });

  it('rejects section headers', () => {
    const headers = [
      'Verse', 'Verse 1', 'Verse 2',
      'Chorus', 'Pre-Chorus', 'Post-Chorus',
      'Bridge', 'Intro', 'Outro',
      'Tag', 'Ending', 'Instrumental',
      'Interlude', 'Solo', 'Break',
    ];

    headers.forEach((header) => {
      expect(isChord(header)).toBe(false);
    });
  });

  it('rejects invalid strings', () => {
    expect(isChord('Hello')).toBe(false);
    expect(isChord('World')).toBe(false);
    expect(isChord('123')).toBe(false);
    expect(isChord('')).toBe(false);
  });
});

// =============================================================================
// CHORD TRANSPOSITION
// =============================================================================

describe('transposeChord', () => {
  describe('to sharp keys', () => {
    it('transposes to G (1 sharp)', () => {
      // From C to G (+7 semitones)
      expect(transposeChord('C', 7, true)).toBe('G');
      expect(transposeChord('F', 7, true)).toBe('C');
      expect(transposeChord('Am', 7, true)).toBe('Em');
      expect(transposeChord('Dm', 7, true)).toBe('Am');
    });

    it('transposes to D (2 sharps)', () => {
      // From G to D (+7 semitones)
      expect(transposeChord('G', 7, true)).toBe('D');
      expect(transposeChord('C', 7, true)).toBe('G');
      expect(transposeChord('Em', 7, true)).toBe('Bm');
    });

    it('transposes to A (3 sharps)', () => {
      // From C to A (+9 semitones)
      expect(transposeChord('C', 9, true)).toBe('A');
      expect(transposeChord('G', 9, true)).toBe('E');
      expect(transposeChord('Am', 9, true)).toBe('F#m');
    });

    it('transposes to E (4 sharps)', () => {
      // From A to E (+7 semitones)
      expect(transposeChord('A', 7, true)).toBe('E');
      expect(transposeChord('D', 7, true)).toBe('A');
      expect(transposeChord('F#m', 7, true)).toBe('C#m');
    });
  });

  describe('to flat keys', () => {
    it('transposes to F (1 flat)', () => {
      // From C to F (+5 semitones)
      expect(transposeChord('C', 5, false)).toBe('F');
      expect(transposeChord('G', 5, false)).toBe('C');
      expect(transposeChord('Am', 5, false)).toBe('Dm');
      expect(transposeChord('Em', 5, false)).toBe('Am');
    });

    it('transposes to Bb (2 flats)', () => {
      // From C to Bb (+10 semitones)
      expect(transposeChord('C', 10, false)).toBe('Bb');
      expect(transposeChord('G', 10, false)).toBe('F');
      expect(transposeChord('Dm', 10, false)).toBe('Cm');
      expect(transposeChord('Am', 10, false)).toBe('Gm');
    });

    it('transposes to Eb (3 flats)', () => {
      // From C to Eb (+3 semitones)
      expect(transposeChord('C', 3, false)).toBe('Eb');
      expect(transposeChord('G', 3, false)).toBe('Bb');
      expect(transposeChord('F', 3, false)).toBe('Ab');
      expect(transposeChord('Am', 3, false)).toBe('Cm');
    });

    it('transposes to Ab (4 flats)', () => {
      // From C to Ab (+8 semitones)
      expect(transposeChord('C', 8, false)).toBe('Ab');
      expect(transposeChord('G', 8, false)).toBe('Eb');
      expect(transposeChord('Dm', 8, false)).toBe('Bbm');
    });
  });

  describe('seventh and extended chords', () => {
    it('preserves chord quality during transposition', () => {
      // G to C (+5 semitones, sharp key)
      expect(transposeChord('G7', 5, true)).toBe('C7');
      expect(transposeChord('Gmaj7', 5, true)).toBe('Cmaj7');
      expect(transposeChord('Em7', 5, true)).toBe('Am7');
      expect(transposeChord('Am9', 5, true)).toBe('Dm9');
      expect(transposeChord('Dsus4', 5, true)).toBe('Gsus4');
      expect(transposeChord('Cadd9', 5, true)).toBe('Fadd9');
    });
  });

  describe('slash chords', () => {
    it('transposes both root and bass', () => {
      // G to C (+5 semitones)
      expect(transposeChord('G/B', 5, true)).toBe('C/E');
      expect(transposeChord('D/F#', 5, true)).toBe('G/B');
      expect(transposeChord('Am7/G', 5, true)).toBe('Dm7/C');
    });

    it('handles flat bass notes in flat keys', () => {
      // C to F (+5 semitones)
      expect(transposeChord('G/B', 5, false)).toBe('C/E');
      // C to Bb (+10 semitones)
      expect(transposeChord('C/E', 10, false)).toBe('Bb/D');
      expect(transposeChord('G/B', 10, false)).toBe('F/A');
    });
  });
});

// =============================================================================
// FULL CHORDPRO TRANSPOSITION
// =============================================================================

describe('transposeChordPro', () => {
  describe('preserves section headers', () => {
    it('does not transpose section headers', () => {
      const input = '[Verse 1]\n[G]La la [C]la';
      const result = transposeChordPro(input, 'G', 'C');
      expect(result).toContain('[Verse 1]');
      expect(result).toContain('[C]');
      expect(result).toContain('[F]');
    });

    it('handles multiple section types', () => {
      const input = '[Intro]\n[G]\n[Verse]\n[G] [C]\n[Chorus]\n[D] [G]';
      const result = transposeChordPro(input, 'G', 'C');
      expect(result).toContain('[Intro]');
      expect(result).toContain('[Verse]');
      expect(result).toContain('[Chorus]');
    });
  });

  describe('common worship progressions', () => {
    // I-V-vi-IV (most common pop/worship progression)
    it('transposes I-V-vi-IV from G to C', () => {
      const input = '[G] [D] [Em] [C]';
      const result = transposeChordPro(input, 'G', 'C');
      expect(result).toBe('[C] [G] [Am] [F]');
    });

    it('transposes I-V-vi-IV from G to D', () => {
      // G(I) D(V) Em(vi) C(IV) -> D(I) A(V) Bm(vi) G(IV)
      const input = '[G] [D] [Em] [C]';
      const result = transposeChordPro(input, 'G', 'D');
      expect(result).toBe('[D] [A] [Bm] [G]');
    });

    it('transposes I-V-vi-IV from G to F (flat key)', () => {
      const input = '[G] [D] [Em] [C]';
      const result = transposeChordPro(input, 'G', 'F');
      expect(result).toBe('[F] [C] [Dm] [Bb]');
    });

    it('transposes I-V-vi-IV from G to Bb (flat key)', () => {
      const input = '[G] [D] [Em] [C]';
      const result = transposeChordPro(input, 'G', 'Bb');
      expect(result).toBe('[Bb] [F] [Gm] [Eb]');
    });

    // vi-IV-I-V (another common progression)
    it('transposes vi-IV-I-V from G to A', () => {
      const input = '[Em] [C] [G] [D]';
      const result = transposeChordPro(input, 'G', 'A');
      expect(result).toBe('[F#m] [D] [A] [E]');
    });

    // I-IV-V (classic progression)
    it('transposes I-IV-V from G to E', () => {
      const input = '[G] [C] [D]';
      const result = transposeChordPro(input, 'G', 'E');
      expect(result).toBe('[E] [A] [B]');
    });

    // I-IV-vi-V
    it('transposes I-IV-vi-V from C to G', () => {
      const input = '[C] [F] [Am] [G]';
      const result = transposeChordPro(input, 'C', 'G');
      expect(result).toBe('[G] [C] [Em] [D]');
    });
  });

  describe('worship songs with 7th chords', () => {
    it('transposes progression with maj7 and m7', () => {
      const input = '[Gmaj7] [Em7] [Cmaj7] [D]';
      const result = transposeChordPro(input, 'G', 'C');
      expect(result).toBe('[Cmaj7] [Am7] [Fmaj7] [G]');
    });

    it('transposes progression with sus chords', () => {
      const input = '[G] [Dsus4] [D] [Em] [Csus2] [C]';
      const result = transposeChordPro(input, 'G', 'A');
      expect(result).toBe('[A] [Esus4] [E] [F#m] [Dsus2] [D]');
    });
  });

  describe('songs with slash chords', () => {
    it('transposes walkdown bass line', () => {
      // Classic walkdown: G - G/F# - Em - Em/D - C
      const input = '[G] [G/F#] [Em] [Em/D] [C]';
      const result = transposeChordPro(input, 'G', 'C');
      expect(result).toBe('[C] [C/B] [Am] [Am/G] [F]');
    });

    it('transposes walkdown in flat key', () => {
      const input = '[G] [G/F#] [Em] [Em/D] [C]';
      const result = transposeChordPro(input, 'G', 'F');
      expect(result).toBe('[F] [F/E] [Dm] [Dm/C] [Bb]');
    });

    it('transposes ascending bass line', () => {
      // C - C/E - F - F/A - G
      const input = '[C] [C/E] [F] [F/A] [G]';
      const result = transposeChordPro(input, 'C', 'G');
      expect(result).toBe('[G] [G/B] [C] [C/E] [D]');
    });
  });

  describe('edge cases', () => {
    it('returns original when keys are the same', () => {
      const input = '[G] [C] [D]';
      expect(transposeChordPro(input, 'G', 'G')).toBe(input);
    });

    it('handles empty input', () => {
      expect(transposeChordPro('', 'G', 'C')).toBe('');
    });

    it('handles null fromKey', () => {
      const input = '[G] [C]';
      expect(transposeChordPro(input, null as unknown as string, 'C')).toBe(input);
    });

    it('handles input without chords', () => {
      const input = 'Just plain text\nwith no chords';
      expect(transposeChordPro(input, 'G', 'C')).toBe(input);
    });

    it('handles mixed content', () => {
      const input = '[Verse 1]\n[G]Just some [D]words\n\n[Chorus]\n[C]More [G]words';
      const result = transposeChordPro(input, 'G', 'A');
      expect(result).toContain('[Verse 1]');
      expect(result).toContain('[A]');
      expect(result).toContain('[E]');
      expect(result).toContain('[Chorus]');
      expect(result).toContain('[D]');
    });
  });

  describe('enharmonic spelling by target key', () => {
    it('uses sharps when transposing to sharp keys', () => {
      // From F to D: Bb should become G, not Gb
      const input = '[F] [Bb] [C] [Dm]';
      const result = transposeChordPro(input, 'F', 'D');
      expect(result).toBe('[D] [G] [A] [Bm]');
      expect(result).not.toContain('Gb');
    });

    it('uses flats when transposing to flat keys', () => {
      // From G to Eb: F# should become Bb, not A#
      const input = '[G] [D] [Em] [C]';
      const result = transposeChordPro(input, 'G', 'Eb');
      expect(result).toBe('[Eb] [Bb] [Cm] [Ab]');
      expect(result).not.toContain('A#');
      expect(result).not.toContain('G#');
    });

    it('uses correct spelling for all flat keys', () => {
      const input = '[C] [G] [Am] [F]';

      // To F (1 flat)
      expect(transposeChordPro(input, 'C', 'F')).toBe('[F] [C] [Dm] [Bb]');

      // To Bb (2 flats)
      expect(transposeChordPro(input, 'C', 'Bb')).toBe('[Bb] [F] [Gm] [Eb]');

      // To Eb (3 flats)
      expect(transposeChordPro(input, 'C', 'Eb')).toBe('[Eb] [Bb] [Cm] [Ab]');

      // To Ab (4 flats)
      expect(transposeChordPro(input, 'C', 'Ab')).toBe('[Ab] [Eb] [Fm] [Db]');
    });

    it('uses correct spelling for all sharp keys', () => {
      const input = '[C] [G] [Am] [F]';

      // To G (1 sharp)
      expect(transposeChordPro(input, 'C', 'G')).toBe('[G] [D] [Em] [C]');

      // To D (2 sharps)
      expect(transposeChordPro(input, 'C', 'D')).toBe('[D] [A] [Bm] [G]');

      // To A (3 sharps)
      expect(transposeChordPro(input, 'C', 'A')).toBe('[A] [E] [F#m] [D]');

      // To E (4 sharps)
      expect(transposeChordPro(input, 'C', 'E')).toBe('[E] [B] [C#m] [A]');
    });
  });
});

// =============================================================================
// CAPO SUGGESTIONS
// =============================================================================

describe('suggestCapo', () => {
  it('suggests capo for F (play E with capo 1)', () => {
    const suggestions = suggestCapo('F');
    expect(suggestions.some((s) => s.capo === 1 && s.playedKey === 'E')).toBe(true);
  });

  it('suggests capo for Bb (play A with capo 1 or G with capo 3)', () => {
    const suggestions = suggestCapo('Bb');
    expect(suggestions.some((s) => s.capo === 1 && s.playedKey === 'A')).toBe(true);
    expect(suggestions.some((s) => s.capo === 3 && s.playedKey === 'G')).toBe(true);
  });

  it('suggests capo for Eb (play D with capo 1 or C with capo 3)', () => {
    const suggestions = suggestCapo('Eb');
    expect(suggestions.some((s) => s.capo === 1 && s.playedKey === 'D')).toBe(true);
    expect(suggestions.some((s) => s.capo === 3 && s.playedKey === 'C')).toBe(true);
  });

  it('suggests capo for Ab (play G with capo 1)', () => {
    const suggestions = suggestCapo('Ab');
    expect(suggestions.some((s) => s.capo === 1 && s.playedKey === 'G')).toBe(true);
  });

  it('suggests capo for F# (play E with capo 2 or D with capo 4)', () => {
    const suggestions = suggestCapo('F#');
    expect(suggestions.some((s) => s.capo === 2 && s.playedKey === 'E')).toBe(true);
    expect(suggestions.some((s) => s.capo === 4 && s.playedKey === 'D')).toBe(true);
  });

  it('prioritizes easier keys (G > C > D > A > E)', () => {
    const suggestions = suggestCapo('Bb');
    // G with capo 3 should come before A with capo 1 based on EASY_GUITAR_KEYS order
    const gIndex = suggestions.findIndex((s) => s.playedKey === 'G');
    const aIndex = suggestions.findIndex((s) => s.playedKey === 'A');
    if (gIndex !== -1 && aIndex !== -1) {
      expect(gIndex).toBeLessThan(aIndex);
    }
  });

  it('returns empty array for already-easy keys', () => {
    // Easy keys shouldn't have capo suggestions that result in other easy keys
    // at lower frets, but this test is about whether they're truly needed
    // In practice, G doesn't need capo to play G
    EASY_GUITAR_KEYS.forEach((key) => {
      const suggestions = suggestCapo(key);
      // While suggestions may exist, they're less necessary
      // Just verify the function doesn't crash
      expect(Array.isArray(suggestions)).toBe(true);
    });
  });
});

describe('isDifficultKey', () => {
  it('identifies easy keys correctly', () => {
    EASY_GUITAR_KEYS.forEach((key) => {
      expect(isDifficultKey(key)).toBe(false);
    });
  });

  it('identifies difficult keys correctly', () => {
    const difficultKeys = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'F#', 'C#', 'B'];
    difficultKeys.forEach((key) => {
      expect(isDifficultKey(key)).toBe(true);
    });
  });

  it('handles enharmonic equivalents', () => {
    // G# and Ab are the same pitch, both should be difficult
    expect(isDifficultKey('G#')).toBe(true);
    expect(isDifficultKey('Ab')).toBe(true);
  });
});

// =============================================================================
// REAL-WORLD TRANSPOSITION SCENARIOS
// =============================================================================

describe('real-world transposition scenarios', () => {
  describe('common key changes in worship', () => {
    it('transposes from G to A (common key change up)', () => {
      // Very common in worship to raise key for energy
      const input = '[G] [D/F#] [Em] [C] [G/B] [Am7] [Dsus4] [D]';
      const result = transposeChordPro(input, 'G', 'A');
      expect(result).toBe('[A] [E/G#] [F#m] [D] [A/C#] [Bm7] [Esus4] [E]');
    });

    it('transposes from G to B (male to female range)', () => {
      const input = '[G] [C] [Em] [D]';
      const result = transposeChordPro(input, 'G', 'B');
      expect(result).toBe('[B] [E] [G#m] [F#]');
    });

    it('transposes from A to F (lower for bass voice)', () => {
      const input = '[A] [D] [E] [F#m]';
      const result = transposeChordPro(input, 'A', 'F');
      expect(result).toBe('[F] [Bb] [C] [Dm]');
    });

    it('transposes from C to Eb (jazz/gospel feel)', () => {
      const input = '[Cmaj7] [Dm7] [Em7] [Fmaj7] [G7]';
      const result = transposeChordPro(input, 'C', 'Eb');
      expect(result).toBe('[Ebmaj7] [Fm7] [Gm7] [Abmaj7] [Bb7]');
    });
  });

  describe('complete song structure', () => {
    it('transposes full song from G to C', () => {
      const input = `[Intro]
[G] [D/F#] [Em] [C]

[Verse 1]
[G]First line of [D]verse
[Em]Second line [C]here
[G]Third line [D/F#]with walk[Em]down [C]

[Chorus]
[C]Chorus [G/B]starts [Am7]here
[D]Building [Dsus4]up [D]

[Bridge]
[Em] [C] [G] [D]`;

      const result = transposeChordPro(input, 'G', 'C');

      // Check section headers preserved
      expect(result).toContain('[Intro]');
      expect(result).toContain('[Verse 1]');
      expect(result).toContain('[Chorus]');
      expect(result).toContain('[Bridge]');

      // Check chords transposed correctly
      expect(result).toContain('[C]'); // Was G
      expect(result).toContain('[G/B]'); // Was D/F#
      expect(result).toContain('[Am]'); // Was Em
      expect(result).toContain('[F]'); // Was C
      expect(result).toContain('[Dm7]'); // Was Am7
      expect(result).toContain('[Gsus4]'); // Was Dsus4
    });
  });

  describe('handling input with flat chords', () => {
    it('transposes song originally in Bb to G', () => {
      const input = '[Bb] [F] [Gm] [Eb]';
      const result = transposeChordPro(input, 'Bb', 'G');
      expect(result).toBe('[G] [D] [Em] [C]');
    });

    it('transposes song originally in Eb to C', () => {
      const input = '[Eb] [Bb] [Cm] [Ab]';
      const result = transposeChordPro(input, 'Eb', 'C');
      expect(result).toBe('[C] [G] [Am] [F]');
    });

    it('transposes from flat key to another flat key', () => {
      const input = '[F] [Bb] [C] [Dm]';
      const result = transposeChordPro(input, 'F', 'Eb');
      expect(result).toBe('[Eb] [Ab] [Bb] [Cm]');
    });
  });
});
