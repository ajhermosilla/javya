import type { MusicalKey, Song, SongCreate } from './song';

export type ImportFormat =
  | 'chordpro'
  | 'openlyrics'
  | 'opensong'
  | 'onsong'
  | 'ultimateguitar'
  | 'plaintext'
  | 'unknown';

export enum ImportAction {
  CREATE = 'create',
  MERGE = 'merge',
  SKIP = 'skip',
}

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

export interface SongImportItem {
  song_data: SongCreate;
  action: ImportAction;
  existing_song_id?: string;
}

export interface ImportConfirmRequest {
  songs: SongImportItem[];
}

export interface ImportConfirmResponse {
  created_count: number;
  merged_count: number;
  skipped_count: number;
  songs: Song[];
}
