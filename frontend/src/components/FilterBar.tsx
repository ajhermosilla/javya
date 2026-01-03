import { useTranslation } from 'react-i18next';
import type { MusicalKey, Mood, Theme } from '../types/song';
import './FilterBar.css';

const KEYS: MusicalKey[] = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const MOODS: Mood[] = ['Joyful', 'Reflective', 'Triumphant', 'Intimate', 'Peaceful', 'Energetic', 'Hopeful', 'Solemn', 'Celebratory'];
const THEMES: Theme[] = ['Worship', 'Communion', 'Offering', 'Opening', 'Closing', 'Prayer', 'Declaration', 'Thanksgiving', 'Faith', 'Grace', 'Salvation', 'Baptism', 'Christmas', 'Holy Week'];

interface FilterBarProps {
  keyFilter?: MusicalKey;
  moodFilter?: Mood;
  themeFilter?: Theme;
  onKeyChange: (key?: MusicalKey) => void;
  onMoodChange: (mood?: Mood) => void;
  onThemeChange: (theme?: Theme) => void;
}

export function FilterBar({
  keyFilter,
  moodFilter,
  themeFilter,
  onKeyChange,
  onMoodChange,
  onThemeChange,
}: FilterBarProps) {
  const { t } = useTranslation();

  return (
    <div className="filter-bar">
      <select
        value={keyFilter || ''}
        onChange={(e) => onKeyChange(e.target.value as MusicalKey || undefined)}
        className="filter-select"
      >
        <option value="">{t('form.originalKey')}</option>
        {KEYS.map(key => (
          <option key={key} value={key}>{t(`keys.${key}`)}</option>
        ))}
      </select>

      <select
        value={moodFilter || ''}
        onChange={(e) => onMoodChange(e.target.value as Mood || undefined)}
        className="filter-select"
      >
        <option value="">{t('form.mood')}</option>
        {MOODS.map(mood => (
          <option key={mood} value={mood}>{t(`moods.${mood}`)}</option>
        ))}
      </select>

      <select
        value={themeFilter || ''}
        onChange={(e) => onThemeChange(e.target.value as Theme || undefined)}
        className="filter-select"
      >
        <option value="">{t('form.themes')}</option>
        {THEMES.map(theme => (
          <option key={theme} value={theme}>{t(`themes.${theme}`)}</option>
        ))}
      </select>
    </div>
  );
}
