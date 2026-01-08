import type { MusicalKey, Song, SongCreate } from './song';

export type ImportFormat =
  | 'chordpro'
  | 'openlyrics'
  | 'opensong'
  | 'plaintext'
  | 'unknown';

export interface ExistingSongSummary {
  id: string;
  name: string;
  artist: string | null;
  original_key: MusicalKey | null;
}

export interface ParsedSong {
  file_name: string;
  detected_format: ImportFormat;
  success: boolean;
  error: string | null;
  song_data: SongCreate | null;
  duplicate: ExistingSongSummary | null;
}

export interface ImportPreviewResponse {
  total_files: number;
  successful: number;
  failed: number;
  songs: ParsedSong[];
}

export interface ImportConfirmRequest {
  songs: SongCreate[];
}

export interface ImportConfirmResponse {
  saved_count: number;
  songs: Song[];
}
