import type { EventType } from './setlist';
import type { AvailabilityStatus } from './availability';

export type ServiceRole =
  | 'worship_leader'
  | 'vocalist'
  | 'guitarist'
  | 'bassist'
  | 'drummer'
  | 'keys'
  | 'sound'
  | 'projection'
  | 'other';

export const SERVICE_ROLES: ServiceRole[] = [
  'worship_leader',
  'vocalist',
  'guitarist',
  'bassist',
  'drummer',
  'keys',
  'sound',
  'projection',
  'other',
];

export interface SetlistAssignment {
  id: string;
  setlist_id: string;
  user_id: string;
  service_role: ServiceRole;
  notes: string | null;
  confirmed: boolean;
  created_at: string;
  updated_at: string;
}

export interface SetlistAssignmentWithUser extends SetlistAssignment {
  user_name: string;
  user_email: string;
}

export interface SetlistAssignmentCreate {
  user_id: string;
  service_role: ServiceRole;
  notes?: string | null;
}

export interface SetlistAssignmentUpdate {
  service_role?: ServiceRole;
  notes?: string | null;
}

export interface CalendarSetlist {
  id: string;
  name: string;
  service_date: string | null;
  event_type: EventType | null;
  song_count: number;
  assignments: {
    id: string;
    user_id: string;
    user_name: string;
    service_role: ServiceRole;
    confirmed: boolean;
  }[];
}

export interface TeamMemberAvailability {
  user_id: string;
  user_name: string;
  user_email: string;
  user_role: string;
  availability_status: AvailabilityStatus | null;
  availability_note: string | null;
}

export interface MyAssignment {
  id: string;
  service_role: ServiceRole;
  notes: string | null;
  confirmed: boolean;
  setlist_id: string;
  setlist_name: string;
  service_date: string | null;
  event_type: EventType | null;
}
