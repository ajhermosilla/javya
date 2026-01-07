import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { MusicalKey } from '../types/song';
import { DISPLAY_KEYS, isDifficultKey, suggestCapo } from '../utils/transpose';
import './TransposeControls.css';

interface TransposeControlsProps {
  originalKey: MusicalKey | null;
  currentKey: MusicalKey;
  onKeyChange: (newKey: MusicalKey) => void;
}

export function TransposeControls({
  originalKey,
  currentKey,
  onKeyChange,
}: TransposeControlsProps) {
  const { t } = useTranslation();

  const capoSuggestions = useMemo(() => {
    if (!isDifficultKey(currentKey)) {
      return [];
    }
    return suggestCapo(currentKey).slice(0, 2);
  }, [currentKey]);

  const isTransposed = originalKey && currentKey !== originalKey;

  return (
    <div className="transpose-controls">
      <div className="transpose-key-select">
        <label htmlFor="transpose-key">{t('transpose.displayKey')}</label>
        <select
          id="transpose-key"
          value={currentKey}
          onChange={(e) => onKeyChange(e.target.value as MusicalKey)}
        >
          {DISPLAY_KEYS.map((key) => (
            <option key={key} value={key}>
              {t(`keys.${key}`)}
            </option>
          ))}
        </select>
        {isTransposed && (
          <button
            type="button"
            className="reset-key-button"
            onClick={() => onKeyChange(originalKey)}
            title={t('transpose.reset')}
          >
            {t('transpose.reset')}
          </button>
        )}
      </div>

      {capoSuggestions.length > 0 && (
        <div className="capo-suggestions">
          <span className="capo-label">{t('transpose.capoSuggestion')}:</span>
          {capoSuggestions.map(({ capo, playedKey }) => (
            <span key={capo} className="capo-badge">
              {t('transpose.capo')} {capo} ({t(`keys.${playedKey}`)})
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
