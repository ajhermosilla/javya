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

  exportFreeshow: async (id: string, filename: string) => {
    const response = await fetch(`${BASE_PATH}/${id}/export/freeshow`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.project`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  exportQuelea: async (id: string, filename: string) => {
    const response = await fetch(`${BASE_PATH}/${id}/export/quelea`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.qsch`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};
