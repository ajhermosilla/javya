import { api, API_BASE_URL, getStoredToken } from './client';
import type { Setlist, SetlistCreate, SetlistUpdate } from '../types/setlist';

const BASE_PATH = '/api/v1/setlists';

/**
 * Build a full URL for export endpoints, respecting API_BASE_URL.
 */
function exportUrl(path: string): string {
  return `${API_BASE_URL}${BASE_PATH}${path}`;
}

/**
 * Build auth headers for export fetch calls.
 */
function authHeaders(): HeadersInit {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

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

/**
 * Fetch an export endpoint and handle common error statuses.
 */
async function fetchExport(path: string): Promise<Blob> {
  const response = await fetch(exportUrl(path), { headers: authHeaders() });
  if (!response.ok) {
    const status = response.status;
    if (status === 401) throw new Error('Authentication required');
    if (status === 404) throw new Error('Setlist not found');
    if (status === 400) throw new Error('Cannot export empty setlist');
    throw new Error(`Export failed (${status})`);
  }
  return response.blob();
}

export const setlistsApi = {
  list: () => api.get<Setlist[]>(`${BASE_PATH}/`),

  get: (id: string) => api.get<Setlist>(`${BASE_PATH}/${id}`),

  create: (data: SetlistCreate) => api.post<Setlist>(`${BASE_PATH}/`, data),

  update: (id: string, data: SetlistUpdate) =>
    api.put<Setlist>(`${BASE_PATH}/${id}`, data),

  delete: (id: string) => api.delete(`${BASE_PATH}/${id}`),

  exportFreeshow: async (id: string, filename: string) => {
    const blob = await fetchExport(`/${id}/export/freeshow`);
    downloadBlob(blob, `${filename}.project`);
  },

  exportQuelea: async (id: string, filename: string) => {
    const blob = await fetchExport(`/${id}/export/quelea`);
    downloadBlob(blob, `${filename}.qsch`);
  },

  exportPdf: async (id: string, filename: string, format: 'summary' | 'chords' = 'summary') => {
    const blob = await fetchExport(`/${id}/export/pdf?format=${format}`);
    const suffix = format === 'summary' ? 'summary' : 'chords';
    downloadBlob(blob, `${filename}-${suffix}.pdf`);
  },
};
