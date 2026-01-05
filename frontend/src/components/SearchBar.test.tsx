import { render, screen } from '../test/utils';
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

  it('calls onChange when typing', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();

    render(
      <SearchBar
        value=""
        onChange={handleChange}
        placeholder="Search..."
      />
    );

    const input = screen.getByPlaceholderText('Search...');
    await user.type(input, 'hello');

    expect(handleChange).toHaveBeenCalledTimes(5);
    expect(handleChange).toHaveBeenLastCalledWith('o');
  });

  it('renders without placeholder', () => {
    render(<SearchBar value="" onChange={() => {}} />);

    const input = screen.getByRole('textbox');
    expect(input).toBeInTheDocument();
  });
});
