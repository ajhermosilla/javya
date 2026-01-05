import { api } from './client';
import type {
  Availability,
  AvailabilityCreate,
  AvailabilityPattern,
  AvailabilityPatternCreate,
  AvailabilityPatternUpdate,
  AvailabilityWithUser,
  BulkAvailabilityCreate,
} from '../types/availability';

const BASE_URL = '/api/v1/availability';

// Date-specific availability
export async function setAvailability(
  data: AvailabilityCreate
): Promise<Availability> {
  return api.post<Availability>(`${BASE_URL}/`, data);
}

export async function setBulkAvailability(
  data: BulkAvailabilityCreate
): Promise<Availability[]> {
  return api.post<Availability[]>(`${BASE_URL}/bulk`, data);
}

export async function getMyAvailability(
  startDate: string,
  endDate: string
): Promise<Availability[]> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });
  return api.get<Availability[]>(`${BASE_URL}/me?${params}`);
}

export async function getTeamAvailability(
  startDate: string,
  endDate: string
): Promise<AvailabilityWithUser[]> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });
  return api.get<AvailabilityWithUser[]>(`${BASE_URL}/team?${params}`);
}

export async function deleteAvailability(id: string): Promise<void> {
  return api.delete(`${BASE_URL}/${id}`);
}

// Availability patterns
export async function createPattern(
  data: AvailabilityPatternCreate
): Promise<AvailabilityPattern> {
  return api.post<AvailabilityPattern>(`${BASE_URL}/patterns`, data);
}

export async function getMyPatterns(): Promise<AvailabilityPattern[]> {
  return api.get<AvailabilityPattern[]>(`${BASE_URL}/patterns`);
}

export async function updatePattern(
  id: string,
  data: AvailabilityPatternUpdate
): Promise<AvailabilityPattern> {
  return api.put<AvailabilityPattern>(`${BASE_URL}/patterns/${id}`, data);
}

export async function deletePattern(id: string): Promise<void> {
  return api.delete(`${BASE_URL}/patterns/${id}`);
}
