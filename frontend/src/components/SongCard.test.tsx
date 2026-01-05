import { render, screen, waitFor } from '../test/utils';
import userEvent from '@testing-library/user-event';
import { SongCard } from './SongCard';
import { mockSong, mockSongMinimal } from '../test/mocks';
import { songsApi } from '../api/songs';

// Mock the songs API
vi.mock('../api/songs', () => ({
  songsApi: {
    delete: vi.fn(),
  },
}));

describe('SongCard', () => {
  const defaultProps = {
    song: mockSong,
    onClick: vi.fn(),
    onEdit: vi.fn(),
    onDelete: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders song name', () => {
    render(<SongCard {...defaultProps} />);

    expect(screen.getByText('Amazing Grace')).toBeInTheDocument();
  });

  it('renders artist when present', () => {
    render(<SongCard {...defaultProps} />);

    expect(screen.getByText('John Newton')).toBeInTheDocument();
  });

  it('does not render artist when absent', () => {
    render(<SongCard {...defaultProps} song={mockSongMinimal} />);

    expect(screen.queryByText('John Newton')).not.toBeInTheDocument();
  });

  it('renders key tag when present', () => {
    render(<SongCard {...defaultProps} />);

    expect(screen.getByText('keys.G')).toBeInTheDocument();
  });

  it('renders mood tag when present', () => {
    render(<SongCard {...defaultProps} />);

    expect(screen.getByText('moods.Reflective')).toBeInTheDocument();
  });

  it('renders tempo when present', () => {
    render(<SongCard {...defaultProps} />);

    expect(screen.getByText('72 BPM')).toBeInTheDocument();
  });

  it('renders theme tags', () => {
    render(<SongCard {...defaultProps} />);

    expect(screen.getByText('themes.Grace')).toBeInTheDocument();
    expect(screen.getByText('themes.Salvation')).toBeInTheDocument();
  });

  it('calls onClick when header is clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<SongCard {...defaultProps} onClick={onClick} />);

    await user.click(screen.getByText('Amazing Grace'));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();
    render(<SongCard {...defaultProps} onEdit={onEdit} />);

    await user.click(screen.getByText('songs.editSong'));

    expect(onEdit).toHaveBeenCalledTimes(1);
  });

  it('shows confirmation dialog when delete is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(songsApi.delete).mockResolvedValue(undefined);

    render(<SongCard {...defaultProps} />);

    await user.click(screen.getByText('songs.deleteSong'));

    expect(global.confirm).toHaveBeenCalledWith('songs.confirmDelete');
  });

  it('calls API delete and onDelete when confirmed', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.mocked(songsApi.delete).mockResolvedValue(undefined);
    vi.mocked(global.confirm).mockReturnValue(true);

    render(<SongCard {...defaultProps} onDelete={onDelete} />);

    await user.click(screen.getByText('songs.deleteSong'));

    await waitFor(() => {
      expect(songsApi.delete).toHaveBeenCalledWith('1');
      expect(onDelete).toHaveBeenCalled();
    });
  });

  it('does not delete when cancelled', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.mocked(global.confirm).mockReturnValue(false);

    render(<SongCard {...defaultProps} onDelete={onDelete} />);

    await user.click(screen.getByText('songs.deleteSong'));

    expect(songsApi.delete).not.toHaveBeenCalled();
    expect(onDelete).not.toHaveBeenCalled();
  });

  it('shows alert on delete error', async () => {
    const user = userEvent.setup();
    vi.mocked(songsApi.delete).mockRejectedValue(new Error('API Error'));
    vi.mocked(global.confirm).mockReturnValue(true);

    render(<SongCard {...defaultProps} />);

    await user.click(screen.getByText('songs.deleteSong'));

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('common.deleteFailed');
    });
  });
});
