import type { Song } from '../types/song';
import type { Setlist, SetlistSong } from '../types/setlist';

export const mockSong: Song = {
  id: '1',
  name: 'Amazing Grace',
  artist: 'John Newton',
  url: 'https://www.youtube.com/watch?v=12345',
  original_key: 'G',
  preferred_key: 'E',
  tempo_bpm: 72,
  mood: 'Reflective',
  themes: ['Grace', 'Salvation'],
  lyrics: 'Amazing grace, how sweet the sound\nThat saved a wretch like me',
  chordpro_chart: '[G]Amazing [G7]grace',
  min_band: ['acoustic guitar', 'vocals'],
  notes: 'Great for communion',
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

export const mockSongMinimal: Song = {
  id: '2',
  name: 'Simple Song',
  artist: null,
  url: null,
  original_key: null,
  preferred_key: null,
  tempo_bpm: null,
  mood: null,
  themes: [],
  lyrics: null,
  chordpro_chart: null,
  min_band: [],
  notes: null,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

export const mockSetlistSong: SetlistSong = {
  id: '1',
  song_id: '1',
  position: 0,
  notes: 'Opening song',
  song: mockSong,
};

export const mockSetlist: Setlist = {
  id: '1',
  name: 'Sunday Service',
  description: 'Regular Sunday morning worship',
  service_date: '2025-01-12',
  event_type: 'Sunday',
  song_count: 1,
  songs: [mockSetlistSong],
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

export const mockSetlistMinimal: Setlist = {
  id: '2',
  name: 'Quick Setlist',
  description: null,
  service_date: null,
  event_type: null,
  song_count: 0,
  songs: [],
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};
