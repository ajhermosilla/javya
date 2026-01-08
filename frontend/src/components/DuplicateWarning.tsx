import { useTranslation } from 'react-i18next';
import type { ExistingSongSummary } from '../api/songs';
import './DuplicateWarning.css';

interface DuplicateWarningProps {
  existingSong: ExistingSongSummary;
  onUseExisting: () => void;
  onCreateAnyway: () => void;
  onCancel: () => void;
}

export function DuplicateWarning({
  existingSong,
  onUseExisting,
  onCreateAnyway,
  onCancel,
}: DuplicateWarningProps) {
  const { t } = useTranslation();

  return (
    <div className="duplicate-warning-overlay" onClick={onCancel}>
      <div
        className="duplicate-warning-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="duplicate-warning-title">{t('duplicates.warning')}</h3>
        <p className="duplicate-warning-text">{t('duplicates.exists')}</p>

        <div className="duplicate-warning-song">
          <strong>{existingSong.name}</strong>
          {existingSong.artist && (
            <span className="duplicate-warning-artist">
              {' '}
              {t('duplicates.by')} {existingSong.artist}
            </span>
          )}
          {existingSong.original_key && (
            <span className="duplicate-warning-key">
              {' '}
              ({t('duplicates.key')}: {existingSong.original_key})
            </span>
          )}
        </div>

        <div className="duplicate-warning-actions">
          <button
            type="button"
            className="duplicate-warning-btn duplicate-warning-btn-secondary"
            onClick={onUseExisting}
          >
            {t('duplicates.useExisting')}
          </button>
          <button
            type="button"
            className="duplicate-warning-btn duplicate-warning-btn-primary"
            onClick={onCreateAnyway}
          >
            {t('duplicates.createAnyway')}
          </button>
        </div>
      </div>
    </div>
  );
}
