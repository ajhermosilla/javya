import { useTranslation } from 'react-i18next';
import type { MusicalKey } from '../types/song';
import './KeyIndicator.css';

interface KeyIndicatorProps {
  specifiedKey: MusicalKey | null;
  detectedKey: MusicalKey | null;
  keyConfidence: 'high' | 'medium' | 'low' | null;
  selectedKey: MusicalKey | null;
  onKeySelect: (key: MusicalKey | null) => void;
}

export function KeyIndicator({
  specifiedKey,
  detectedKey,
  keyConfidence,
  selectedKey,
  onKeySelect,
}: KeyIndicatorProps) {
  const { t } = useTranslation();

  // No keys at all
  if (!specifiedKey && !detectedKey) {
    return <span className="key-indicator-none">—</span>;
  }

  // Only one key exists - no conflict
  if (!specifiedKey && detectedKey) {
    return (
      <div className="key-indicator-single">
        <span className="key-indicator-badge key-indicator-detected">
          {detectedKey}
        </span>
        {keyConfidence && (
          <span className={`key-confidence key-confidence-${keyConfidence}`}>
            {t(`import.keyConfidence.${keyConfidence}`)}
          </span>
        )}
      </div>
    );
  }

  if (specifiedKey && !detectedKey) {
    return (
      <span className="key-indicator-badge key-indicator-specified">
        {specifiedKey}
      </span>
    );
  }

  // Both exist and match
  if (specifiedKey === detectedKey) {
    return (
      <span className="key-indicator-badge key-indicator-match">
        {specifiedKey}
      </span>
    );
  }

  // Both exist but differ - show selection UI
  const currentSelection = selectedKey || specifiedKey;

  return (
    <div className="key-indicator-conflict">
      <button
        type="button"
        className={`key-select-btn ${currentSelection === specifiedKey ? 'active' : ''}`}
        onClick={() => onKeySelect(specifiedKey)}
        title={t('import.keySource.specified')}
      >
        {specifiedKey}
        <span className="key-source-label">{t('import.keySource.file')}</span>
      </button>
      <button
        type="button"
        className={`key-select-btn key-select-detected ${currentSelection === detectedKey ? 'active' : ''}`}
        onClick={() => onKeySelect(detectedKey)}
        title={t('import.keySource.detected')}
      >
        {detectedKey}
        <span className="key-source-label">{t('import.keySource.chords')}</span>
        {keyConfidence && (
          <span className={`key-confidence-inline key-confidence-${keyConfidence}`}>
            {keyConfidence === 'high' ? '!' : keyConfidence === 'medium' ? '?' : '~'}
          </span>
        )}
      </button>
    </div>
  );
}
