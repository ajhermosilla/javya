import { useTranslation } from 'react-i18next';
import type { ImportPreviewResponse } from '../types/import';
import { ImportAction } from '../types/import';
import type { MusicalKey } from '../types/song';
import { KeyIndicator } from './KeyIndicator';
import './ImportPreview.css';

interface ImportPreviewProps {
  data: ImportPreviewResponse;
  selectedIndices: Set<number>;
  onSelectionChange: (indices: Set<number>) => void;
  duplicateActions: Map<number, ImportAction>;
  onDuplicateActionChange: (index: number, action: ImportAction) => void;
  keySelections: Map<number, MusicalKey | null>;
  onKeySelectionChange: (index: number, key: MusicalKey | null) => void;
  onEditSong: (index: number) => void;
  onConfirm: () => void;
  onBack: () => void;
}

const FORMAT_LABELS: Record<string, string> = {
  chordpro: 'ChordPro',
  openlyrics: 'OpenLyrics',
  opensong: 'OpenSong',
  onsong: 'OnSong',
  ultimateguitar: 'Ultimate Guitar',
  plaintext: 'Plain Text',
  unknown: 'Unknown',
};

export function ImportPreview({
  data,
  selectedIndices,
  onSelectionChange,
  duplicateActions,
  onDuplicateActionChange,
  keySelections,
  onKeySelectionChange,
  onEditSong,
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
              <th className="import-col-key">{t('import.preview.key')}</th>
              <th className="import-col-status">
                {t('import.preview.status')}
              </th>
              <th className="import-col-actions"></th>
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
                <td className="import-col-key">
                  {song.success && (
                    <KeyIndicator
                      specifiedKey={song.specified_key}
                      detectedKey={song.detected_key}
                      keyConfidence={song.key_confidence}
                      selectedKey={keySelections.get(index) ?? null}
                      onKeySelect={(key) => onKeySelectionChange(index, key)}
                    />
                  )}
                </td>
                <td className="import-col-status">
                  {song.success ? (
                    song.duplicate ? (
                      <div className="import-duplicate-actions">
                        <span
                          className="import-duplicate-label"
                          title={`${song.duplicate.name}${song.duplicate.artist ? ` - ${song.duplicate.artist}` : ''}`}
                        >
                          {t('import.preview.duplicate')}:
                        </span>
                        <div className="import-action-buttons">
                          <button
                            type="button"
                            className={`import-action-btn ${duplicateActions.get(index) === ImportAction.SKIP ? 'active' : ''}`}
                            onClick={() => onDuplicateActionChange(index, ImportAction.SKIP)}
                            title={t('import.actions.skipDesc')}
                          >
                            {t('import.actions.skip')}
                          </button>
                          <button
                            type="button"
                            className={`import-action-btn import-action-merge ${duplicateActions.get(index) === ImportAction.MERGE ? 'active' : ''}`}
                            onClick={() => onDuplicateActionChange(index, ImportAction.MERGE)}
                            title={t('import.actions.mergeDesc')}
                          >
                            {t('import.actions.merge')}
                          </button>
                          <button
                            type="button"
                            className={`import-action-btn ${duplicateActions.get(index) === ImportAction.CREATE ? 'active' : ''}`}
                            onClick={() => onDuplicateActionChange(index, ImportAction.CREATE)}
                            title={t('import.actions.createDesc')}
                          >
                            {t('import.actions.create')}
                          </button>
                        </div>
                      </div>
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
                <td className="import-col-actions">
                  {song.success && song.song_data && (
                    <button
                      className="import-edit-button"
                      onClick={() => onEditSong(index)}
                      title={t('import.edit.title')}
                      type="button"
                    >
                      {t('common.edit')}
                    </button>
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
