import { api } from './client';
import type { Setlist, SetlistCreate, SetlistUpdate } from '../types/setlist';

const BASE_PATH = '/api/v1/setlists';

/**
 * Download a blob as a file with proper cleanup.
 */
function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  try {
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
  } finally {
    if (a.parentNode) {
      document.body.removeChild(a);
    }
    URL.revokeObjectURL(url);
  }
}

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
    downloadBlob(blob, `${filename}.project`);
  },

  exportQuelea: async (id: string, filename: string) => {
    const response = await fetch(`${BASE_PATH}/${id}/export/quelea`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    const blob = await response.blob();
    downloadBlob(blob, `${filename}.qsch`);
  },
};
