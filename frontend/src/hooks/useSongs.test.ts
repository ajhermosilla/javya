import { renderHook, waitFor, act } from '@testing-library/react';
import { useSongs } from './useSongs';
import { songsApi } from '../api/songs';
import { mockSong, mockSongMinimal } from '../test/mocks';

// Mock the songs API
vi.mock('../api/songs', () => ({
  songsApi: {
    list: vi.fn(),
  },
}));

describe('useSongs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('starts with loading state', () => {
    vi.mocked(songsApi.list).mockImplementation(() => new Promise(() => {}));

    const { result } = renderHook(() => useSongs());

    expect(result.current.loading).toBe(true);
    expect(result.current.songs).toEqual([]);
    expect(result.current.error).toBe(null);
  });

  it('fetches songs on mount', async () => {
    const mockSongs = [mockSong, mockSongMinimal];
    vi.mocked(songsApi.list).mockResolvedValue(mockSongs);

    const { result } = renderHook(() => useSongs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.songs).toEqual(mockSongs);
    expect(result.current.error).toBe(null);
    expect(songsApi.list).toHaveBeenCalledWith({});
  });

  it('passes filters to API', async () => {
    vi.mocked(songsApi.list).mockResolvedValue([]);

    const filters = {
      search: 'grace',
      key: 'G' as const,
      mood: 'Joyful' as const,
      theme: 'Worship' as const,
    };

    const { result } = renderHook(() => useSongs(filters));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(songsApi.list).toHaveBeenCalledWith(filters);
  });

  it('handles API errors', async () => {
    vi.mocked(songsApi.list).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useSongs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.songs).toEqual([]);
    expect(result.current.error).toBe('Network error');
  });

  it('handles non-Error exceptions', async () => {
    vi.mocked(songsApi.list).mockRejectedValue('Unknown error');

    const { result } = renderHook(() => useSongs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to fetch songs');
  });

  it('refetches when filters change', async () => {
    vi.mocked(songsApi.list).mockResolvedValue([mockSong]);

    const { result, rerender } = renderHook(
      ({ filters }) => useSongs(filters),
      { initialProps: { filters: {} } }
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(songsApi.list).toHaveBeenCalledTimes(1);

    rerender({ filters: { search: 'test' } });

    await waitFor(() => {
      expect(songsApi.list).toHaveBeenCalledTimes(2);
    });

    expect(songsApi.list).toHaveBeenLastCalledWith({ search: 'test' });
  });

  it('provides refetch function', async () => {
    vi.mocked(songsApi.list).mockResolvedValue([mockSong]);

    const { result } = renderHook(() => useSongs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(songsApi.list).toHaveBeenCalledTimes(1);

    await act(async () => {
      await result.current.refetch();
    });

    expect(songsApi.list).toHaveBeenCalledTimes(2);
  });
});
