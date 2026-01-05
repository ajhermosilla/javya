import { api } from './client';
import type {
  CalendarSetlist,
  MyAssignment,
  SetlistAssignment,
  SetlistAssignmentCreate,
  SetlistAssignmentUpdate,
  SetlistAssignmentWithUser,
  TeamMemberAvailability,
} from '../types/scheduling';

const SETLISTS_URL = '/api/v1/setlists';
const SCHEDULING_URL = '/api/v1/scheduling';

// Assignment CRUD (nested under setlists)
export async function getAssignments(
  setlistId: string
): Promise<SetlistAssignmentWithUser[]> {
  return api.get<SetlistAssignmentWithUser[]>(
    `${SETLISTS_URL}/${setlistId}/assignments`
  );
}

export async function createAssignment(
  setlistId: string,
  data: SetlistAssignmentCreate
): Promise<SetlistAssignment> {
  return api.post<SetlistAssignment>(
    `${SETLISTS_URL}/${setlistId}/assignments`,
    data
  );
}

export async function updateAssignment(
  setlistId: string,
  assignmentId: string,
  data: SetlistAssignmentUpdate
): Promise<SetlistAssignment> {
  return api.put<SetlistAssignment>(
    `${SETLISTS_URL}/${setlistId}/assignments/${assignmentId}`,
    data
  );
}

export async function deleteAssignment(
  setlistId: string,
  assignmentId: string
): Promise<void> {
  return api.delete(`${SETLISTS_URL}/${setlistId}/assignments/${assignmentId}`);
}

export async function confirmAssignment(
  setlistId: string,
  assignmentId: string,
  confirmed: boolean
): Promise<SetlistAssignment> {
  return api.patch<SetlistAssignment>(
    `${SETLISTS_URL}/${setlistId}/assignments/${assignmentId}/confirm`,
    { confirmed }
  );
}

// Scheduling endpoints
export async function getCalendar(
  startDate: string,
  endDate: string
): Promise<CalendarSetlist[]> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });
  return api.get<CalendarSetlist[]>(`${SCHEDULING_URL}/calendar?${params}`);
}

export async function getTeamAvailabilityForDate(
  serviceDate: string
): Promise<TeamMemberAvailability[]> {
  const params = new URLSearchParams({
    service_date: serviceDate,
  });
  return api.get<TeamMemberAvailability[]>(
    `${SCHEDULING_URL}/availability?${params}`
  );
}

export async function getMyAssignments(
  upcomingOnly = true
): Promise<MyAssignment[]> {
  const params = new URLSearchParams({
    upcoming_only: upcomingOnly.toString(),
  });
  return api.get<MyAssignment[]>(`${SCHEDULING_URL}/my-assignments?${params}`);
}
