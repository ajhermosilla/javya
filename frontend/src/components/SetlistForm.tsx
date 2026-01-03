import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Setlist, SetlistCreate, EventType } from '../types/setlist';
import './SetlistForm.css';

const EVENT_TYPES: EventType[] = ['Sunday', 'Wednesday', 'Youth', 'Special', 'Retreat', 'Other'];

interface SetlistFormProps {
  setlist?: Setlist;
  onSubmit: (data: SetlistCreate) => Promise<void>;
  onCancel: () => void;
}

export function SetlistForm({ setlist, onSubmit, onCancel }: SetlistFormProps) {
  const { t } = useTranslation();
  const [name, setName] = useState(setlist?.name ?? '');
  const [description, setDescription] = useState(setlist?.description ?? '');
  const [serviceDate, setServiceDate] = useState(setlist?.service_date ?? '');
  const [eventType, setEventType] = useState<EventType | ''>(setlist?.event_type ?? '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      await onSubmit({
        name,
        description: description || null,
        service_date: serviceDate || null,
        event_type: eventType || null,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save setlist');
      setSaving(false);
    }
  };

  const isEditing = !!setlist;

  return (
    <form className="setlist-form" onSubmit={handleSubmit}>
      <h2>{isEditing ? t('setlists.editSetlist') : t('setlists.addSetlist')}</h2>

      {error && <div className="form-error">{error}</div>}

      <div className="form-group">
        <label htmlFor="name">
          {t('form.name')} <span className="required">*</span>
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={255}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="serviceDate">{t('setlistForm.serviceDate')}</label>
          <input
            id="serviceDate"
            type="date"
            value={serviceDate}
            onChange={(e) => setServiceDate(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="eventType">{t('setlistForm.eventType')}</label>
          <select
            id="eventType"
            value={eventType}
            onChange={(e) => setEventType(e.target.value as EventType | '')}
          >
            <option value="">{t('common.select')}</option>
            {EVENT_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(`eventTypes.${type}`)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="description">{t('setlistForm.description')}</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
        />
      </div>

      <div className="form-actions">
        <button type="button" className="cancel-button" onClick={onCancel}>
          {t('form.cancel')}
        </button>
        <button type="submit" className="submit-button" disabled={saving || !name.trim()}>
          {saving ? t('form.saving') : t('form.save')}
        </button>
      </div>
    </form>
  );
}
