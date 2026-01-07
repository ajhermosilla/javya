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

// Notes in chromatic order using sharps
export const SHARP_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] as const;

// Notes in chromatic order using flats
export const FLAT_NOTES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'] as const;

// Keys that use sharp notation (Circle of Fifths clockwise)
export const SHARP_KEYS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#'] as const;

// Keys that use flat notation (Circle of Fifths counter-clockwise)
export const FLAT_KEYS = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb'] as const;

// "Easy" keys for guitar - open chord shapes
export const EASY_GUITAR_KEYS = ['G', 'C', 'D', 'A', 'E'] as const;

// Map enharmonic equivalents to semitone index
const NOTE_TO_SEMITONE: Record<string, number> = {
  'C': 0, 'B#': 0,
  'C#': 1, 'Db': 1,
  'D': 2,
  'D#': 3, 'Eb': 3,
  'E': 4, 'Fb': 4,
  'F': 5, 'E#': 5,
  'F#': 6, 'Gb': 6,
  'G': 7,
  'G#': 8, 'Ab': 8,
  'A': 9,
  'A#': 10, 'Bb': 10,
  'B': 11, 'Cb': 11,
};

/**
 * Check if a key uses sharp notation.
 */
export function usesSharps(key: string): boolean {
  const normalized = normalizeKeyName(key);
  return SHARP_KEYS.includes(normalized as typeof SHARP_KEYS[number]);
}

/**
 * Normalize key name to standard format (capitalize first letter).
 */
function normalizeKeyName(key: string): string {
  if (!key) return key;
  return key.charAt(0).toUpperCase() + key.slice(1).toLowerCase();
}

/**
 * Get semitone index (0-11) for a note.
 * Handles both sharp and flat notation.
 */
export function noteToSemitone(note: string): number {
  const normalized = normalizeKeyName(note);
  const semitone = NOTE_TO_SEMITONE[normalized];
  if (semitone === undefined) {
    throw new Error(`Invalid note: ${note}`);
  }
  return semitone;
}

/**
 * Convert semitone index to note name using appropriate spelling.
 */
export function semitoneToNote(semitone: number, useSharps: boolean): string {
  const index = ((semitone % 12) + 12) % 12;
  return useSharps ? SHARP_NOTES[index] : FLAT_NOTES[index];
}

/**
 * Calculate semitone interval between two keys.
 */
export function calculateInterval(fromKey: string, toKey: string): number {
  const fromSemitone = noteToSemitone(fromKey);
  const toSemitone = noteToSemitone(toKey);
  return ((toSemitone - fromSemitone) + 12) % 12;
}

/**
 * Transpose a single note by a number of semitones.
 */
export function transposeNote(note: string, semitones: number, useSharps: boolean): string {
  const currentSemitone = noteToSemitone(note);
  return semitoneToNote(currentSemitone + semitones, useSharps);
}

/**
 * Parsed chord components.
 */
export interface ChordComponents {
  root: string;
  quality: string;
  bass: string | null;
}

/**
 * Parse a chord into its components.
 * Examples:
 *   "G" -> { root: "G", quality: "", bass: null }
 *   "Am7" -> { root: "A", quality: "m7", bass: null }
 *   "F#m/C#" -> { root: "F#", quality: "m", bass: "C#" }
 */
export function parseChord(chord: string): ChordComponents | null {
  // Handle slash chords (bass note)
  const slashIndex = chord.lastIndexOf('/');
  let mainChord = chord;
  let bass: string | null = null;

  if (slashIndex > 0) {
    mainChord = chord.substring(0, slashIndex);
    bass = chord.substring(slashIndex + 1);
    // Validate bass note
    if (!/^[A-Ga-g][#b]?$/.test(bass)) {
      return null;
    }
  }

  // Parse root note and quality
  const match = mainChord.match(/^([A-Ga-g])([#b]?)(.*)$/);
  if (!match) {
    return null;
  }

  const [, rootLetter, accidental, quality] = match;
  const root = rootLetter.toUpperCase() + accidental;

  return { root, quality, bass };
}

/**
 * Transpose a single chord by a number of semitones.
 */
export function transposeChord(chord: string, semitones: number, useSharps: boolean): string {
  const components = parseChord(chord);
  if (!components) {
    // Not a valid chord, return as-is
    return chord;
  }

  const newRoot = transposeNote(components.root, semitones, useSharps);
  let result = newRoot + components.quality;

  if (components.bass) {
    const newBass = transposeNote(components.bass, semitones, useSharps);
    result += '/' + newBass;
  }

  return result;
}

/**
 * Check if a bracketed string is a chord (vs section header like [Verse]).
 */
export function isChord(content: string): boolean {
  // Chord pattern: root note + optional accidental + optional quality + optional bass
  const chordPattern = /^[A-Ga-g][#b]?(m|maj|min|dim|aug|sus|add|[0-9])*(\/[A-Ga-g][#b]?)?$/;
  return chordPattern.test(content);
}

/**
 * Transpose all chords in a ChordPro string.
 * Section headers like [Verse 1] are preserved unchanged.
 */
export function transposeChordPro(
  chordpro: string,
  fromKey: string,
  toKey: string
): string {
  if (!chordpro || !fromKey || fromKey === toKey) {
    return chordpro;
  }

  const semitones = calculateInterval(fromKey, toKey);
  const useSharps = usesSharps(toKey);

  // Replace all bracketed content that is a chord
  return chordpro.replace(/\[([^\]]+)\]/g, (match, content) => {
    if (isChord(content)) {
      return '[' + transposeChord(content, semitones, useSharps) + ']';
    }
    // Section header, return unchanged
    return match;
  });
}

/**
 * Capo suggestion with played key.
 */
export interface CapoSuggestion {
  capo: number;
  playedKey: string;
}

/**
 * Calculate what key the guitarist would play if using a capo.
 * If target is F and capo is on fret 1, play E shapes.
 */
export function getPlayedKey(targetKey: string, capoFret: number): string {
  const targetSemitone = noteToSemitone(targetKey);
  // Playing with capo means the shapes are lower by capo semitones
  const playedSemitone = (targetSemitone - capoFret + 12) % 12;
  // Return the played key using sharps (guitar convention)
  return semitoneToNote(playedSemitone, true);
}

/**
 * Suggest capo positions for a target key.
 * Returns positions where the played key is one of the easy guitar keys.
 */
export function suggestCapo(targetKey: string): CapoSuggestion[] {
  const suggestions: CapoSuggestion[] = [];

  // Check capo positions 1-7 (beyond 7 gets uncomfortable)
  for (let capo = 1; capo <= 7; capo++) {
    const playedKey = getPlayedKey(targetKey, capo);
    if (EASY_GUITAR_KEYS.includes(playedKey as typeof EASY_GUITAR_KEYS[number])) {
      suggestions.push({ capo, playedKey });
    }
  }

  // Sort by ease of played key (G > C > D > A > E) then by lower capo
  suggestions.sort((a, b) => {
    const aRank = EASY_GUITAR_KEYS.indexOf(a.playedKey as typeof EASY_GUITAR_KEYS[number]);
    const bRank = EASY_GUITAR_KEYS.indexOf(b.playedKey as typeof EASY_GUITAR_KEYS[number]);
    if (aRank !== bRank) return aRank - bRank;
    return a.capo - b.capo;
  });

  return suggestions;
}

/**
 * Check if a key is considered "difficult" for guitar (needs barre chords).
 */
export function isDifficultKey(key: string): boolean {
  try {
    const semitone = noteToSemitone(key);
    const normalizedKey = semitoneToNote(semitone, true);
    return !EASY_GUITAR_KEYS.includes(normalizedKey as typeof EASY_GUITAR_KEYS[number]);
  } catch {
    return false;
  }
}

/**
 * Get the display-friendly key order for dropdowns.
 * Circle of Fifths order: sharps clockwise, flats counter-clockwise.
 */
export const DISPLAY_KEYS = [
  'C', 'G', 'D', 'A', 'E', 'B', 'F#',  // Sharp keys
  'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb',   // Flat keys
] as const;
