export type MusicalKey =
  | 'C' | 'C#' | 'D' | 'D#' | 'E' | 'F'
  | 'F#' | 'G' | 'G#' | 'A' | 'A#' | 'B';

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
