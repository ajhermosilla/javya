import { render, screen, waitFor } from '../test/utils';
import userEvent from '@testing-library/user-event';
import { SetlistCard } from './SetlistCard';
import { mockSetlist, mockSetlistMinimal } from '../test/mocks';
import { setlistsApi } from '../api/setlists';

// Mock the setlists API
vi.mock('../api/setlists', () => ({
  setlistsApi: {
    delete: vi.fn(),
  },
}));

describe('SetlistCard', () => {
  const defaultProps = {
    setlist: mockSetlist,
    onClick: vi.fn(),
    onEdit: vi.fn(),
    onDelete: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders setlist name', () => {
    render(<SetlistCard {...defaultProps} />);

    expect(screen.getByText('Sunday Service')).toBeInTheDocument();
  });

  it('renders formatted date when present', () => {
    render(<SetlistCard {...defaultProps} />);

    // Date format depends on locale, just check it's there
    expect(screen.getByText(/1\/12\/2025|12\/1\/2025|2025/)).toBeInTheDocument();
  });

  it('does not render date when absent', () => {
    render(<SetlistCard {...defaultProps} setlist={mockSetlistMinimal} />);

    expect(screen.queryByText(/2025/)).not.toBeInTheDocument();
  });

  it('renders event type tag when present', () => {
    render(<SetlistCard {...defaultProps} />);

    expect(screen.getByText('eventTypes.Sunday')).toBeInTheDocument();
  });

  it('renders song count', () => {
    render(<SetlistCard {...defaultProps} />);

    expect(screen.getByText('1 song')).toBeInTheDocument();
  });

  it('renders plural songs for count > 1', () => {
    const setlistWithMultipleSongs = {
      ...mockSetlist,
      song_count: 5,
    };
    render(<SetlistCard {...defaultProps} setlist={setlistWithMultipleSongs} />);

    expect(screen.getByText('5 songs')).toBeInTheDocument();
  });

  it('renders description when present', () => {
    render(<SetlistCard {...defaultProps} />);

    expect(screen.getByText('Regular Sunday morning worship')).toBeInTheDocument();
  });

  it('calls onClick when header is clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<SetlistCard {...defaultProps} onClick={onClick} />);

    await user.click(screen.getByText('Sunday Service'));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();
    render(<SetlistCard {...defaultProps} onEdit={onEdit} />);

    await user.click(screen.getByText('setlists.editSetlist'));

    expect(onEdit).toHaveBeenCalledTimes(1);
  });

  it('shows confirmation dialog when delete is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(setlistsApi.delete).mockResolvedValue(undefined);

    render(<SetlistCard {...defaultProps} />);

    await user.click(screen.getByText('setlists.deleteSetlist'));

    expect(global.confirm).toHaveBeenCalledWith('setlists.confirmDelete');
  });

  it('calls API delete and onDelete when confirmed', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.mocked(setlistsApi.delete).mockResolvedValue(undefined);
    vi.mocked(global.confirm).mockReturnValue(true);

    render(<SetlistCard {...defaultProps} onDelete={onDelete} />);

    await user.click(screen.getByText('setlists.deleteSetlist'));

    await waitFor(() => {
      expect(setlistsApi.delete).toHaveBeenCalledWith('1');
      expect(onDelete).toHaveBeenCalled();
    });
  });

  it('does not delete when cancelled', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.mocked(global.confirm).mockReturnValue(false);

    render(<SetlistCard {...defaultProps} onDelete={onDelete} />);

    await user.click(screen.getByText('setlists.deleteSetlist'));

    expect(setlistsApi.delete).not.toHaveBeenCalled();
    expect(onDelete).not.toHaveBeenCalled();
  });

  it('shows alert on delete error', async () => {
    const user = userEvent.setup();
    vi.mocked(setlistsApi.delete).mockRejectedValue(new Error('API Error'));
    vi.mocked(global.confirm).mockReturnValue(true);

    render(<SetlistCard {...defaultProps} />);

    await user.click(screen.getByText('setlists.deleteSetlist'));

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('common.deleteFailed');
    });
  });
});
