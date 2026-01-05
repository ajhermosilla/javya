export type AvailabilityStatus = 'available' | 'unavailable' | 'maybe';
export type PatternType = 'weekly' | 'biweekly' | 'monthly';

export interface Availability {
  id: string;
  user_id: string;
  date: string;
  status: AvailabilityStatus;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export interface AvailabilityWithUser extends Availability {
  user_name: string;
  user_email: string;
}

export interface AvailabilityCreate {
  date: string;
  status: AvailabilityStatus;
  note?: string | null;
}

export interface BulkAvailabilityCreate {
  entries: AvailabilityCreate[];
}

export interface AvailabilityPattern {
  id: string;
  user_id: string;
  pattern_type: PatternType;
  day_of_week: number; // 0=Monday, 6=Sunday
  status: AvailabilityStatus;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export interface AvailabilityPatternCreate {
  pattern_type: PatternType;
  day_of_week: number;
  status: AvailabilityStatus;
  start_date?: string | null;
  end_date?: string | null;
  note?: string | null;
}

export interface AvailabilityPatternUpdate {
  pattern_type?: PatternType;
  day_of_week?: number;
  status?: AvailabilityStatus;
  start_date?: string | null;
  end_date?: string | null;
  is_active?: boolean;
  note?: string | null;
}

export const DAY_NAMES = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
] as const;
