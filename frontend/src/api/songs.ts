import { api } from './client';
import type { Song, SongCreate, SongUpdate, SongFilters } from '../types/song';
import type { ExistingSongSummary } from '../types/import';

const BASE_PATH = '/api/v1/songs';

interface SongCheck {
  name: string;
  artist: string | null;
}

interface DuplicateMatch {
  index: number;
  name: string;
  artist: string | null;
  existing_song: ExistingSongSummary;
}

interface CheckDuplicatesResponse {
  duplicates: DuplicateMatch[];
}

function buildQueryString(filters: SongFilters): string {
  const params = new URLSearchParams();

  if (filters.search) params.append('search', filters.search);
  if (filters.key) params.append('key', filters.key);
  if (filters.mood) params.append('mood', filters.mood);
  if (filters.theme) params.append('theme', filters.theme);

  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

export const songsApi = {
  list: (filters: SongFilters = {}) =>
    api.get<Song[]>(`${BASE_PATH}/${buildQueryString(filters)}`),

  get: (id: string) =>
    api.get<Song>(`${BASE_PATH}/${id}`),

  create: (data: SongCreate) =>
    api.post<Song>(`${BASE_PATH}/`, data),

  update: (id: string, data: SongUpdate) =>
    api.put<Song>(`${BASE_PATH}/${id}`, data),

  delete: (id: string) =>
    api.delete(`${BASE_PATH}/${id}`),

  checkDuplicates: (songs: SongCheck[]) =>
    api.post<CheckDuplicatesResponse>(`${BASE_PATH}/check-duplicates`, { songs }),
};

export type { ExistingSongSummary };
