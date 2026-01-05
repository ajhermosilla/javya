import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type {
  AvailabilityPattern,
  AvailabilityPatternCreate,
  AvailabilityPatternUpdate,
  AvailabilityStatus,
  PatternType,
} from '../types/availability';
import './PatternEditor.css';

interface PatternEditorProps {
  patterns: AvailabilityPattern[];
  onCreate: (data: AvailabilityPatternCreate) => Promise<AvailabilityPattern>;
  onUpdate: (id: string, data: AvailabilityPatternUpdate) => Promise<AvailabilityPattern>;
  onDelete: (id: string) => Promise<void>;
}

const DAYS_OF_WEEK = [0, 1, 2, 3, 4, 5, 6] as const;
const PATTERN_TYPES: PatternType[] = ['weekly', 'biweekly', 'monthly'];
const STATUSES: AvailabilityStatus[] = ['available', 'unavailable', 'maybe'];

export function PatternEditor({
  patterns,
  onCreate,
  onUpdate,
  onDelete,
}: PatternEditorProps) {
  const { t } = useTranslation();
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState<AvailabilityPatternCreate>({
    pattern_type: 'weekly',
    day_of_week: 0,
    status: 'available',
  });

  const weekdayNames = [
    t('availability.weekdays.mon'),
    t('availability.weekdays.tue'),
    t('availability.weekdays.wed'),
    t('availability.weekdays.thu'),
    t('availability.weekdays.fri'),
    t('availability.weekdays.sat'),
    t('availability.weekdays.sun'),
  ];

  const handleCreate = async () => {
    await onCreate(formData);
    setIsCreating(false);
    setFormData({ pattern_type: 'weekly', day_of_week: 0, status: 'available' });
  };

  const handleUpdate = async (id: string) => {
    await onUpdate(id, formData);
    setEditingId(null);
    setFormData({ pattern_type: 'weekly', day_of_week: 0, status: 'available' });
  };

  const handleDelete = async (id: string) => {
    await onDelete(id);
  };

  const startEdit = (pattern: AvailabilityPattern) => {
    setEditingId(pattern.id);
    setFormData({
      pattern_type: pattern.pattern_type,
      day_of_week: pattern.day_of_week,
      status: pattern.status,
      note: pattern.note || undefined,
      start_date: pattern.start_date || undefined,
      end_date: pattern.end_date || undefined,
    });
  };

  const toggleActive = async (pattern: AvailabilityPattern) => {
    await onUpdate(pattern.id, { is_active: !pattern.is_active });
  };

  const renderForm = (onSubmit: () => void, submitLabel: string) => (
    <div className="pattern-form">
      <div className="form-row">
        <label>
          {t('availability.patterns.dayOfWeek')}
          <select
            value={formData.day_of_week}
            onChange={(e) =>
              setFormData({ ...formData, day_of_week: Number(e.target.value) })
            }
          >
            {DAYS_OF_WEEK.map((day) => (
              <option key={day} value={day}>
                {weekdayNames[day]}
              </option>
            ))}
          </select>
        </label>

        <label>
          {t('availability.patterns.patternType')}
          <select
            value={formData.pattern_type}
            onChange={(e) =>
              setFormData({
                ...formData,
                pattern_type: e.target.value as PatternType,
              })
            }
          >
            {PATTERN_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(`availability.patterns.types.${type}`)}
              </option>
            ))}
          </select>
        </label>

        <label>
          {t('availability.patterns.status')}
          <select
            value={formData.status}
            onChange={(e) =>
              setFormData({
                ...formData,
                status: e.target.value as AvailabilityStatus,
              })
            }
          >
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {t(`availability.status.${status}`)}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="form-row">
        <label>
          {t('availability.patterns.startDate')}
          <input
            type="date"
            value={formData.start_date || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                start_date: e.target.value || undefined,
              })
            }
          />
        </label>

        <label>
          {t('availability.patterns.endDate')}
          <input
            type="date"
            value={formData.end_date || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                end_date: e.target.value || undefined,
              })
            }
          />
        </label>
      </div>

      <div className="form-row">
        <label className="note-label">
          {t('availability.patterns.note')}
          <input
            type="text"
            value={formData.note || ''}
            onChange={(e) =>
              setFormData({ ...formData, note: e.target.value || undefined })
            }
            placeholder={t('availability.patterns.notePlaceholder')}
          />
        </label>
      </div>

      <div className="form-actions">
        <button className="btn-primary" onClick={onSubmit}>
          {submitLabel}
        </button>
        <button
          className="btn-secondary"
          onClick={() => {
            setIsCreating(false);
            setEditingId(null);
            setFormData({ pattern_type: 'weekly', day_of_week: 0, status: 'available' });
          }}
        >
          {t('common.cancel')}
        </button>
      </div>
    </div>
  );

  return (
    <div className="pattern-editor">
      <div className="pattern-header">
        <h2>{t('availability.patterns.title')}</h2>
        {!isCreating && !editingId && (
          <button className="btn-primary" onClick={() => setIsCreating(true)}>
            {t('availability.patterns.add')}
          </button>
        )}
      </div>

      {isCreating && renderForm(handleCreate, t('common.create'))}

      <div className="patterns-list">
        {patterns.length === 0 && !isCreating && (
          <p className="no-patterns">{t('availability.patterns.empty')}</p>
        )}

        {patterns.map((pattern) => (
          <div
            key={pattern.id}
            className={`pattern-item ${pattern.is_active ? '' : 'inactive'}`}
          >
            {editingId === pattern.id ? (
              renderForm(
                () => handleUpdate(pattern.id),
                t('common.save')
              )
            ) : (
              <>
                <div className="pattern-info">
                  <span className={`status-badge ${pattern.status}`}>
                    {t(`availability.status.${pattern.status}`)}
                  </span>
                  <span className="pattern-day">{weekdayNames[pattern.day_of_week]}</span>
                  <span className="pattern-type">
                    ({t(`availability.patterns.types.${pattern.pattern_type}`)})
                  </span>
                  {pattern.note && (
                    <span className="pattern-note">- {pattern.note}</span>
                  )}
                </div>
                <div className="pattern-actions">
                  <button
                    className="btn-icon"
                    onClick={() => toggleActive(pattern)}
                    title={
                      pattern.is_active
                        ? t('availability.patterns.deactivate')
                        : t('availability.patterns.activate')
                    }
                  >
                    {pattern.is_active ? '✓' : '○'}
                  </button>
                  <button
                    className="btn-icon"
                    onClick={() => startEdit(pattern)}
                    title={t('common.edit')}
                  >
                    ✎
                  </button>
                  <button
                    className="btn-icon delete"
                    onClick={() => handleDelete(pattern.id)}
                    title={t('common.delete')}
                  >
                    ×
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
