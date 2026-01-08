import type {
  ImportPreviewResponse,
  ImportConfirmRequest,
  ImportConfirmResponse,
} from '../types/import';
import { getStoredToken, ApiError } from './client';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Upload files for import preview.
 * Files are parsed but NOT saved to the database.
 */
export async function previewImport(
  files: File[]
): Promise<ImportPreviewResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const token = getStoredToken();
  const response = await fetch(
    `${API_BASE_URL}/api/v1/songs/import/preview`,
    {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: 'Upload failed' }));
    throw new ApiError(response.status, error.detail || 'Upload failed');
  }

  return response.json();
}

/**
 * Import from URL preview.
 * Content is fetched and parsed but NOT saved to the database.
 */
export async function previewUrlImport(
  url: string
): Promise<ImportPreviewResponse> {
  const token = getStoredToken();
  const response = await fetch(
    `${API_BASE_URL}/api/v1/songs/import/preview-url`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ url }),
    }
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: 'URL import failed' }));
    throw new ApiError(response.status, error.detail || 'URL import failed');
  }

  return response.json();
}

/**
 * Confirm and save selected songs from preview.
 */
export async function confirmImport(
  request: ImportConfirmRequest
): Promise<ImportConfirmResponse> {
  const token = getStoredToken();
  const response = await fetch(
    `${API_BASE_URL}/api/v1/songs/import/confirm`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: 'Save failed' }));
    throw new ApiError(response.status, error.detail || 'Save failed');
  }

  return response.json();
}

export const importApi = {
  preview: previewImport,
  previewUrl: previewUrlImport,
  confirm: confirmImport,
};
