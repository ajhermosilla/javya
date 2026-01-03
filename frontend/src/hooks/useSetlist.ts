import { useState, useEffect, useCallback } from 'react';
import { setlistsApi } from '../api/setlists';
import type { Setlist } from '../types/setlist';

interface UseSetlistResult {
  setlist: Setlist | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSetlist(id: string | null): UseSetlistResult {
  const [setlist, setSetlist] = useState<Setlist | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSetlist = useCallback(async () => {
    if (!id) {
      setSetlist(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await setlistsApi.get(id);
      setSetlist(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch setlist');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchSetlist();
  }, [fetchSetlist]);

  return { setlist, loading, error, refetch: fetchSetlist };
}
