import { renderHook, waitFor, act } from '@testing-library/react';
import { useSetlists } from './useSetlists';
import { setlistsApi } from '../api/setlists';
import { mockSetlist, mockSetlistMinimal } from '../test/mocks';

// Mock the setlists API
vi.mock('../api/setlists', () => ({
  setlistsApi: {
    list: vi.fn(),
  },
}));

describe('useSetlists', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('starts with loading state', () => {
    vi.mocked(setlistsApi.list).mockImplementation(() => new Promise(() => {}));

    const { result } = renderHook(() => useSetlists());

    expect(result.current.loading).toBe(true);
    expect(result.current.setlists).toEqual([]);
    expect(result.current.error).toBe(null);
  });

  it('fetches setlists on mount', async () => {
    const mockSetlists = [mockSetlist, mockSetlistMinimal];
    vi.mocked(setlistsApi.list).mockResolvedValue(mockSetlists);

    const { result } = renderHook(() => useSetlists());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.setlists).toEqual(mockSetlists);
    expect(result.current.error).toBe(null);
    expect(setlistsApi.list).toHaveBeenCalledTimes(1);
  });

  it('handles API errors', async () => {
    vi.mocked(setlistsApi.list).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useSetlists());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.setlists).toEqual([]);
    expect(result.current.error).toBe('Network error');
  });

  it('handles non-Error exceptions', async () => {
    vi.mocked(setlistsApi.list).mockRejectedValue('Unknown error');

    const { result } = renderHook(() => useSetlists());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to fetch setlists');
  });

  it('provides refetch function', async () => {
    vi.mocked(setlistsApi.list).mockResolvedValue([mockSetlist]);

    const { result } = renderHook(() => useSetlists());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(setlistsApi.list).toHaveBeenCalledTimes(1);

    await act(async () => {
      await result.current.refetch();
    });

    expect(setlistsApi.list).toHaveBeenCalledTimes(2);
  });

  it('updates setlists after refetch', async () => {
    vi.mocked(setlistsApi.list)
      .mockResolvedValueOnce([mockSetlist])
      .mockResolvedValueOnce([mockSetlist, mockSetlistMinimal]);

    const { result } = renderHook(() => useSetlists());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.setlists).toHaveLength(1);

    await act(async () => {
      await result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.setlists).toHaveLength(2);
    });
  });
});
