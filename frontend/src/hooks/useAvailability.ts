import { useState, useEffect, useCallback } from 'react';
import {
  getMyAvailability,
  getTeamAvailability,
  getMyPatterns,
  setAvailability as apiSetAvailability,
  deleteAvailability as apiDeleteAvailability,
  createPattern as apiCreatePattern,
  updatePattern as apiUpdatePattern,
  deletePattern as apiDeletePattern,
} from '../api/availability';
import type {
  Availability,
  AvailabilityCreate,
  AvailabilityPattern,
  AvailabilityPatternCreate,
  AvailabilityPatternUpdate,
  AvailabilityWithUser,
} from '../types/availability';

interface UseAvailabilityOptions {
  startDate: string;
  endDate: string;
  isTeamView?: boolean;
}

export function useAvailability({
  startDate,
  endDate,
  isTeamView = false,
}: UseAvailabilityOptions) {
  const [availability, setAvailability] = useState<
    Availability[] | AvailabilityWithUser[]
  >([]);
  const [patterns, setPatterns] = useState<AvailabilityPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAvailability = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [availData, patternData] = await Promise.all([
        isTeamView
          ? getTeamAvailability(startDate, endDate)
          : getMyAvailability(startDate, endDate),
        isTeamView ? Promise.resolve([]) : getMyPatterns(),
      ]);

      setAvailability(availData);
      setPatterns(patternData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load availability');
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, isTeamView]);

  useEffect(() => {
    fetchAvailability();
  }, [fetchAvailability]);

  const setDateAvailability = async (data: AvailabilityCreate) => {
    const result = await apiSetAvailability(data);
    await fetchAvailability();
    return result;
  };

  const deleteAvailability = async (id: string) => {
    await apiDeleteAvailability(id);
    await fetchAvailability();
  };

  const createPattern = async (data: AvailabilityPatternCreate) => {
    const result = await apiCreatePattern(data);
    await fetchAvailability();
    return result;
  };

  const updatePattern = async (id: string, data: AvailabilityPatternUpdate) => {
    const result = await apiUpdatePattern(id, data);
    await fetchAvailability();
    return result;
  };

  const deletePattern = async (id: string) => {
    await apiDeletePattern(id);
    await fetchAvailability();
  };

  return {
    availability,
    patterns,
    loading,
    error,
    refetch: fetchAvailability,
    setDateAvailability,
    deleteAvailability,
    createPattern,
    updatePattern,
    deletePattern,
  };
}
