import { useState, useEffect, useCallback } from 'react';
import { setlistsApi } from '../api/setlists';
import type { Setlist } from '../types/setlist';

interface UseSetlistsResult {
  setlists: Setlist[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSetlists(): UseSetlistsResult {
  const [setlists, setSetlists] = useState<Setlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSetlists = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await setlistsApi.list();
      setSetlists(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch setlists');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSetlists();
  }, [fetchSetlists]);

  return { setlists, loading, error, refetch: fetchSetlists };
}
