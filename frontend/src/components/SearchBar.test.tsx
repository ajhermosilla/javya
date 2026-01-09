import { render, screen, waitFor } from '../test/utils';
import userEvent from '@testing-library/user-event';
import { SearchBar } from './SearchBar';

describe('SearchBar', () => {
  it('renders with placeholder', () => {
    render(
      <SearchBar
        value=""
        onChange={() => {}}
        placeholder="Search songs..."
      />
    );

    expect(screen.getByPlaceholderText('Search songs...')).toBeInTheDocument();
  });

  it('displays the current value', () => {
    render(
      <SearchBar
        value="test query"
        onChange={() => {}}
        placeholder="Search..."
      />
    );

    expect(screen.getByDisplayValue('test query')).toBeInTheDocument();
  });

  it('calls onChange after debounce when typing', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();

    render(
      <SearchBar
        value=""
        onChange={handleChange}
        placeholder="Search..."
        debounceMs={50}
      />
    );

    const input = screen.getByPlaceholderText('Search...');
    await user.type(input, 'hello');

    // onChange should not be called immediately due to debounce
    expect(handleChange).not.toHaveBeenCalled();

    // Wait for debounce to complete
    await waitFor(() => {
      expect(handleChange).toHaveBeenCalledTimes(1);
    });
    expect(handleChange).toHaveBeenCalledWith('hello');
  });

  it('renders without placeholder', () => {
    render(<SearchBar value="" onChange={() => {}} />);

    const input = screen.getByRole('textbox');
    expect(input).toBeInTheDocument();
  });
});
