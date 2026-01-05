import type { Song } from './song';

export type EventType = 'Sunday' | 'Wednesday' | 'Youth' | 'Special' | 'Retreat' | 'Other';

export interface SetlistSong {
  id: string;
  song_id: string;
  position: number;
  notes: string | null;
  song: Song;
}

export interface Setlist {
  id: string;
  name: string;
  description: string | null;
  service_date: string | null;
  event_type: EventType | null;
  song_count: number;
  created_at: string;
  updated_at: string;
  songs?: SetlistSong[];
}

export interface SetlistSongCreate {
  song_id: string;
  position: number;
  notes?: string | null;
}

export interface SetlistCreate {
  name: string;
  description?: string | null;
  service_date?: string | null;
  event_type?: EventType | null;
  songs?: SetlistSongCreate[];
}

export type SetlistUpdate = SetlistCreate;
