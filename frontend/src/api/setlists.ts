import { api, getStoredToken } from './client';
import type { Setlist, SetlistCreate, SetlistUpdate } from '../types/setlist';

const BASE_PATH = '/api/v1/setlists';

/**
 * Download a blob as a file with proper cleanup and error handling.
 */
function downloadBlob(blob: Blob, filename: string): void {
  let url: string | null = null;
  let a: HTMLAnchorElement | null = null;

  try {
    url = URL.createObjectURL(blob);
    a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    throw new Error(`Failed to download file: ${message}`);
  } finally {
    if (a?.parentNode) {
      document.body.removeChild(a);
    }
    if (url) {
      URL.revokeObjectURL(url);
    }
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
    const token = getStoredToken();
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(`${BASE_PATH}/${id}/export/freeshow`, { headers });
    if (!response.ok) {
      const status = response.status;
      if (status === 401) {
        throw new Error('Authentication required');
      }
      if (status === 404) {
        throw new Error('Setlist not found');
      }
      throw new Error(`Export failed (${status})`);
    }
    const blob = await response.blob();
    downloadBlob(blob, `${filename}.project`);
  },

  exportQuelea: async (id: string, filename: string) => {
    const token = getStoredToken();
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(`${BASE_PATH}/${id}/export/quelea`, { headers });
    if (!response.ok) {
      const status = response.status;
      if (status === 401) {
        throw new Error('Authentication required');
      }
      if (status === 404) {
        throw new Error('Setlist not found');
      }
      throw new Error(`Export failed (${status})`);
    }
    const blob = await response.blob();
    downloadBlob(blob, `${filename}.qsch`);
  },

  exportPdf: async (id: string, filename: string, format: 'summary' | 'chords' = 'summary') => {
    const token = getStoredToken();
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(
      `${BASE_PATH}/${id}/export/pdf?format=${format}`,
      { headers }
    );
    if (!response.ok) {
      const status = response.status;
      if (status === 401) {
        throw new Error('Authentication required');
      }
      if (status === 404) {
        throw new Error('Setlist not found');
      }
      if (status === 400) {
        throw new Error('Cannot export empty setlist');
      }
      throw new Error(`Export failed (${status})`);
    }
    const blob = await response.blob();
    const suffix = format === 'summary' ? 'summary' : 'chords';
    downloadBlob(blob, `${filename}-${suffix}.pdf`);
  },
};
