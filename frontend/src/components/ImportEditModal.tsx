import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { SongCreate, MusicalKey } from '../types/song';
import './ImportEditModal.css';

interface ImportEditModalProps {
  song: SongCreate;
  fileName: string;
  onSave: (song: SongCreate) => void;
  onClose: () => void;
}

const MUSICAL_KEYS: MusicalKey[] = [
  'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#',
  'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb',
];

export function ImportEditModal({
  song,
  fileName,
  onSave,
  onClose,
}: ImportEditModalProps) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<SongCreate>({ ...song });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === '' ? null : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;
    onSave(formData);
  };

  return (
    <div className="import-edit-overlay" onClick={onClose}>
      <div className="import-edit-modal" onClick={(e) => e.stopPropagation()}>
        <header className="import-edit-header">
          <h3>{t('import.edit.title')}</h3>
          <span className="import-edit-filename">{fileName}</span>
          <button
            className="import-edit-close"
            onClick={onClose}
            aria-label={t('common.close')}
            type="button"
          >
            &times;
          </button>
        </header>

        <form className="import-edit-form" onSubmit={handleSubmit}>
          <div className="import-edit-row">
            <div className="import-edit-field">
              <label htmlFor="edit-name">{t('form.name')} *</label>
              <input
                id="edit-name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="import-edit-field">
              <label htmlFor="edit-artist">{t('form.artist')}</label>
              <input
                id="edit-artist"
                name="artist"
                type="text"
                value={formData.artist || ''}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="import-edit-row">
            <div className="import-edit-field import-edit-field-small">
              <label htmlFor="edit-key">{t('form.originalKey')}</label>
              <select
                id="edit-key"
                name="original_key"
                value={formData.original_key || ''}
                onChange={handleChange}
              >
                <option value="">{t('common.select')}</option>
                {MUSICAL_KEYS.map((key) => (
                  <option key={key} value={key}>
                    {key}
                  </option>
                ))}
              </select>
            </div>
            <div className="import-edit-field import-edit-field-small">
              <label htmlFor="edit-tempo">{t('form.tempo')}</label>
              <input
                id="edit-tempo"
                name="tempo_bpm"
                type="number"
                min="1"
                max="300"
                value={formData.tempo_bpm || ''}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="import-edit-field">
            <label htmlFor="edit-lyrics">{t('form.lyrics')}</label>
            <textarea
              id="edit-lyrics"
              name="lyrics"
              value={formData.lyrics || ''}
              onChange={handleChange}
              rows={6}
            />
          </div>

          <div className="import-edit-field">
            <label htmlFor="edit-chordpro">{t('form.chordproChart')}</label>
            <textarea
              id="edit-chordpro"
              name="chordpro_chart"
              value={formData.chordpro_chart || ''}
              onChange={handleChange}
              rows={6}
              className="import-edit-mono"
            />
          </div>

          <div className="import-edit-field">
            <label htmlFor="edit-notes">{t('form.notes')}</label>
            <textarea
              id="edit-notes"
              name="notes"
              value={formData.notes || ''}
              onChange={handleChange}
              rows={2}
            />
          </div>

          <div className="import-edit-actions">
            <button
              type="button"
              className="import-edit-cancel"
              onClick={onClose}
            >
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              className="import-edit-save"
              disabled={!formData.name.trim()}
            >
              {t('import.edit.save')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
