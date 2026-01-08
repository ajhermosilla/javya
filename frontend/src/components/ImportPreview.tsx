import { useTranslation } from 'react-i18next';
import type { ImportPreviewResponse } from '../types/import';
import './ImportPreview.css';

interface ImportPreviewProps {
  data: ImportPreviewResponse;
  selectedIndices: Set<number>;
  onSelectionChange: (indices: Set<number>) => void;
  onConfirm: () => void;
  onBack: () => void;
}

const FORMAT_LABELS: Record<string, string> = {
  chordpro: 'ChordPro',
  openlyrics: 'OpenLyrics',
  opensong: 'OpenSong',
  ultimateguitar: 'Ultimate Guitar',
  plaintext: 'Plain Text',
  unknown: 'Unknown',
};

export function ImportPreview({
  data,
  selectedIndices,
  onSelectionChange,
  onConfirm,
  onBack,
}: ImportPreviewProps) {
  const { t } = useTranslation();

  const toggleSelection = (index: number) => {
    const newSelection = new Set(selectedIndices);
    if (newSelection.has(index)) {
      newSelection.delete(index);
    } else {
      newSelection.add(index);
    }
    onSelectionChange(newSelection);
  };

  const selectAll = () => {
    const successIndices = data.songs
      .map((s, i) => (s.success ? i : -1))
      .filter((i) => i >= 0);
    onSelectionChange(new Set(successIndices));
  };

  const deselectAll = () => {
    onSelectionChange(new Set());
  };

  const selectedCount = selectedIndices.size;
  const canConfirm = selectedCount > 0;

  return (
    <div className="import-preview">
      <div className="import-preview-header">
        <p className="import-preview-summary">
          {t('import.preview.summary', {
            successful: data.successful,
            total: data.total_files,
          })}
        </p>
        <div className="import-preview-actions">
          <button
            className="import-preview-action"
            onClick={selectAll}
            type="button"
          >
            {t('import.preview.selectAll')}
          </button>
          <button
            className="import-preview-action"
            onClick={deselectAll}
            type="button"
          >
            {t('import.preview.deselectAll')}
          </button>
        </div>
      </div>

      <div className="import-preview-list">
        <table className="import-preview-table">
          <thead>
            <tr>
              <th className="import-col-select"></th>
              <th className="import-col-file">{t('import.preview.file')}</th>
              <th className="import-col-format">
                {t('import.preview.format')}
              </th>
              <th className="import-col-title">{t('import.preview.title')}</th>
              <th className="import-col-status">
                {t('import.preview.status')}
              </th>
            </tr>
          </thead>
          <tbody>
            {data.songs.map((song, index) => (
              <tr
                key={index}
                className={`import-preview-row ${song.success ? '' : 'import-preview-row-failed'}`}
              >
                <td className="import-col-select">
                  <input
                    type="checkbox"
                    checked={selectedIndices.has(index)}
                    onChange={() => toggleSelection(index)}
                    disabled={!song.success}
                  />
                </td>
                <td className="import-col-file" title={song.file_name}>
                  {song.file_name}
                </td>
                <td className="import-col-format">
                  <span className="import-format-badge">
                    {FORMAT_LABELS[song.detected_format] || song.detected_format}
                  </span>
                </td>
                <td className="import-col-title">
                  {song.success && song.song_data
                    ? song.song_data.name
                    : '—'}
                </td>
                <td className="import-col-status">
                  {song.success ? (
                    song.duplicate ? (
                      <span
                        className="import-status-duplicate"
                        title={`${song.duplicate.name}${song.duplicate.artist ? ` - ${song.duplicate.artist}` : ''}`}
                      >
                        {t('import.preview.duplicate')}
                      </span>
                    ) : (
                      <span className="import-status-success">
                        {t('import.preview.ready')}
                      </span>
                    )
                  ) : (
                    <span
                      className="import-status-failed"
                      title={song.error || undefined}
                    >
                      {t('import.preview.failed')}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="import-preview-footer">
        <button className="import-back-button" onClick={onBack} type="button">
          {t('common.back')}
        </button>
        <button
          className="import-confirm-button"
          onClick={onConfirm}
          disabled={!canConfirm}
          type="button"
        >
          {t('import.preview.confirm', { count: selectedCount })}
        </button>
      </div>
    </div>
  );
}
