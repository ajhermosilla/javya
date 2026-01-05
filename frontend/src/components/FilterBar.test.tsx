import { render, screen } from '../test/utils';
import userEvent from '@testing-library/user-event';
import { FilterBar } from './FilterBar';

describe('FilterBar', () => {
  const defaultProps = {
    onKeyChange: vi.fn(),
    onMoodChange: vi.fn(),
    onThemeChange: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all three filter dropdowns', () => {
    render(<FilterBar {...defaultProps} />);

    const selects = screen.getAllByRole('combobox');
    expect(selects).toHaveLength(3);
  });

  it('displays key filter options', async () => {
    const user = userEvent.setup();
    render(<FilterBar {...defaultProps} />);

    const keySelect = screen.getAllByRole('combobox')[0];
    await user.click(keySelect);

    expect(screen.getByText('keys.C')).toBeInTheDocument();
    expect(screen.getByText('keys.G')).toBeInTheDocument();
  });

  it('calls onKeyChange when key is selected', async () => {
    const user = userEvent.setup();
    const onKeyChange = vi.fn();
    render(<FilterBar {...defaultProps} onKeyChange={onKeyChange} />);

    const keySelect = screen.getAllByRole('combobox')[0];
    await user.selectOptions(keySelect, 'G');

    expect(onKeyChange).toHaveBeenCalledWith('G');
  });

  it('calls onMoodChange when mood is selected', async () => {
    const user = userEvent.setup();
    const onMoodChange = vi.fn();
    render(<FilterBar {...defaultProps} onMoodChange={onMoodChange} />);

    const moodSelect = screen.getAllByRole('combobox')[1];
    await user.selectOptions(moodSelect, 'Joyful');

    expect(onMoodChange).toHaveBeenCalledWith('Joyful');
  });

  it('calls onThemeChange when theme is selected', async () => {
    const user = userEvent.setup();
    const onThemeChange = vi.fn();
    render(<FilterBar {...defaultProps} onThemeChange={onThemeChange} />);

    const themeSelect = screen.getAllByRole('combobox')[2];
    await user.selectOptions(themeSelect, 'Worship');

    expect(onThemeChange).toHaveBeenCalledWith('Worship');
  });

  it('shows selected values', () => {
    render(
      <FilterBar
        {...defaultProps}
        keyFilter="G"
        moodFilter="Joyful"
        themeFilter="Worship"
      />
    );

    const selects = screen.getAllByRole('combobox');
    expect(selects[0]).toHaveValue('G');
    expect(selects[1]).toHaveValue('Joyful');
    expect(selects[2]).toHaveValue('Worship');
  });

  it('clears filter when empty option selected', async () => {
    const user = userEvent.setup();
    const onKeyChange = vi.fn();
    render(
      <FilterBar
        {...defaultProps}
        keyFilter="G"
        onKeyChange={onKeyChange}
      />
    );

    const keySelect = screen.getAllByRole('combobox')[0];
    await user.selectOptions(keySelect, '');

    expect(onKeyChange).toHaveBeenCalledWith(undefined);
  });
});
