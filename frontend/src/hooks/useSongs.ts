import { useState, useEffect, useCallback } from 'react';
import { songsApi } from '../api/songs';
import type { Song, SongFilters } from '../types/song';

interface UseSongsResult {
  songs: Song[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSongs(filters: SongFilters = {}): UseSongsResult {
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSongs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await songsApi.list(filters);
      setSongs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch songs');
    } finally {
      setLoading(false);
    }
  }, [filters.search, filters.key, filters.mood, filters.theme]);

  useEffect(() => {
    fetchSongs();
  }, [fetchSongs]);

  return { songs, loading, error, refetch: fetchSongs };
}
