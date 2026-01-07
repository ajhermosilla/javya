// Musical keys following the Circle of Fifths
// Sharp keys (clockwise): C, G, D, A, E, B, F#, C#
// Flat keys (counter-clockwise): F, Bb, Eb, Ab, Db, Gb
export type MusicalKey =
  | 'C' | 'G' | 'D' | 'A' | 'E' | 'B' | 'F#' | 'C#'  // Sharp keys
  | 'F' | 'Bb' | 'Eb' | 'Ab' | 'Db' | 'Gb'           // Flat keys
  | 'D#' | 'G#' | 'A#';                               // Enharmonic (backward compat)

export type Mood =
  | 'Joyful' | 'Reflective' | 'Triumphant' | 'Intimate'
  | 'Peaceful' | 'Energetic' | 'Hopeful' | 'Solemn' | 'Celebratory';

export type Theme =
  | 'Worship' | 'Communion' | 'Offering' | 'Opening' | 'Closing'
  | 'Prayer' | 'Declaration' | 'Thanksgiving' | 'Faith' | 'Grace'
  | 'Salvation' | 'Baptism' | 'Christmas' | 'Holy Week';

export interface Song {
  id: string;
  name: string;
  artist: string | null;
  url: string | null;
  original_key: MusicalKey | null;
  preferred_key: MusicalKey | null;
  tempo_bpm: number | null;
  mood: Mood | null;
  themes: Theme[] | null;
  lyrics: string | null;
  chordpro_chart: string | null;
  min_band: string[] | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface SongCreate {
  name: string;
  artist?: string | null;
  url?: string | null;
  original_key?: MusicalKey | null;
  preferred_key?: MusicalKey | null;
  tempo_bpm?: number | null;
  mood?: Mood | null;
  themes?: Theme[] | null;
  lyrics?: string | null;
  chordpro_chart?: string | null;
  min_band?: string[] | null;
  notes?: string | null;
}

export type SongUpdate = SongCreate;

export interface SongFilters {
  search?: string;
  key?: MusicalKey;
  mood?: Mood;
  theme?: Theme;
}
