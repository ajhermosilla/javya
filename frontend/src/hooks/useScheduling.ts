import { useState, useEffect, useCallback } from 'react';
import {
  getCalendar,
  getMyAssignments,
  getTeamAvailabilityForDate,
  getAssignments,
  createAssignment as apiCreateAssignment,
  updateAssignment as apiUpdateAssignment,
  deleteAssignment as apiDeleteAssignment,
  confirmAssignment as apiConfirmAssignment,
} from '../api/scheduling';
import type {
  CalendarSetlist,
  MyAssignment,
  SetlistAssignmentCreate,
  SetlistAssignmentUpdate,
  SetlistAssignmentWithUser,
  TeamMemberAvailability,
} from '../types/scheduling';

interface UseCalendarOptions {
  startDate: string;
  endDate: string;
}

export function useCalendar({ startDate, endDate }: UseCalendarOptions) {
  const [setlists, setSetlists] = useState<CalendarSetlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCalendar = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCalendar(startDate, endDate);
      setSetlists(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load calendar');
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  return {
    setlists,
    loading,
    error,
    refetch: fetchCalendar,
  };
}

export function useMyAssignments(upcomingOnly = true) {
  const [assignments, setAssignments] = useState<MyAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAssignments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMyAssignments(upcomingOnly);
      setAssignments(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to load assignments'
      );
    } finally {
      setLoading(false);
    }
  }, [upcomingOnly]);

  useEffect(() => {
    fetchAssignments();
  }, [fetchAssignments]);

  const confirmMyAssignment = async (
    setlistId: string,
    assignmentId: string,
    confirmed: boolean
  ) => {
    await apiConfirmAssignment(setlistId, assignmentId, confirmed);
    await fetchAssignments();
  };

  return {
    assignments,
    loading,
    error,
    refetch: fetchAssignments,
    confirmMyAssignment,
  };
}

export function useTeamAvailability(serviceDate: string | null) {
  const [teamAvailability, setTeamAvailability] = useState<
    TeamMemberAvailability[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTeamAvailability = useCallback(async () => {
    if (!serviceDate) {
      setTeamAvailability([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getTeamAvailabilityForDate(serviceDate);
      setTeamAvailability(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to load team availability'
      );
    } finally {
      setLoading(false);
    }
  }, [serviceDate]);

  useEffect(() => {
    fetchTeamAvailability();
  }, [fetchTeamAvailability]);

  return {
    teamAvailability,
    loading,
    error,
    refetch: fetchTeamAvailability,
  };
}

export function useSetlistAssignments(setlistId: string | null) {
  const [assignments, setAssignments] = useState<SetlistAssignmentWithUser[]>(
    []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAssignments = useCallback(async () => {
    if (!setlistId) {
      setAssignments([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getAssignments(setlistId);
      setAssignments(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to load assignments'
      );
    } finally {
      setLoading(false);
    }
  }, [setlistId]);

  useEffect(() => {
    fetchAssignments();
  }, [fetchAssignments]);

  const createAssignment = async (data: SetlistAssignmentCreate) => {
    if (!setlistId) throw new Error('No setlist selected');
    const result = await apiCreateAssignment(setlistId, data);
    await fetchAssignments();
    return result;
  };

  const updateAssignment = async (
    assignmentId: string,
    data: SetlistAssignmentUpdate
  ) => {
    if (!setlistId) throw new Error('No setlist selected');
    const result = await apiUpdateAssignment(setlistId, assignmentId, data);
    await fetchAssignments();
    return result;
  };

  const deleteAssignment = async (assignmentId: string) => {
    if (!setlistId) throw new Error('No setlist selected');
    await apiDeleteAssignment(setlistId, assignmentId);
    await fetchAssignments();
  };

  const confirmAssignment = async (
    assignmentId: string,
    confirmed: boolean
  ) => {
    if (!setlistId) throw new Error('No setlist selected');
    const result = await apiConfirmAssignment(setlistId, assignmentId, confirmed);
    await fetchAssignments();
    return result;
  };

  return {
    assignments,
    loading,
    error,
    refetch: fetchAssignments,
    createAssignment,
    updateAssignment,
    deleteAssignment,
    confirmAssignment,
  };
}
