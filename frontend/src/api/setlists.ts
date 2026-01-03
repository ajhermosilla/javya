import { api } from './client';
import type { Setlist, SetlistCreate, SetlistUpdate } from '../types/setlist';

const BASE_PATH = '/api/v1/setlists';

export const setlistsApi = {
  list: () => api.get<Setlist[]>(`${BASE_PATH}/`),

  get: (id: string) => api.get<Setlist>(`${BASE_PATH}/${id}`),

  create: (data: SetlistCreate) => api.post<Setlist>(`${BASE_PATH}/`, data),

  update: (id: string, data: SetlistUpdate) =>
    api.put<Setlist>(`${BASE_PATH}/${id}`, data),

  delete: (id: string) => api.delete(`${BASE_PATH}/${id}`),
};
