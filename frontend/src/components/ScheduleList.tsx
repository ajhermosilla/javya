import { useTranslation } from 'react-i18next';
import { TeamRoster } from './TeamRoster';
import type { CalendarSetlist } from '../types/scheduling';
import './ScheduleList.css';

interface ScheduleListProps {
  setlists: CalendarSetlist[];
  onSetlistClick: (setlistId: string) => void;
  onAssignmentClick?: (setlistId: string, assignmentId: string) => void;
}

export function ScheduleList({
  setlists,
  onSetlistClick,
  onAssignmentClick,
}: ScheduleListProps) {
  const { t } = useTranslation();

  if (setlists.length === 0) {
    return (
      <div className="schedule-list empty">
        <p>{t('scheduling.noSetlists')}</p>
      </div>
    );
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return t('scheduling.noDate');
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString(undefined, {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="schedule-list">
      {setlists.map((setlist) => (
        <div key={setlist.id} className="schedule-card">
          <div className="card-header" onClick={() => onSetlistClick(setlist.id)}>
            <div className="card-info">
              <h3 className="setlist-name">{setlist.name}</h3>
              <div className="setlist-meta">
                <span className="service-date">
                  {formatDate(setlist.service_date)}
                </span>
                {setlist.event_type && (
                  <span className={`event-type-badge ${setlist.event_type.toLowerCase()}`}>
                    {t(`eventTypes.${setlist.event_type}`)}
                  </span>
                )}
                <span className="song-count">
                  {setlist.song_count} {t('scheduling.songs')}
                </span>
              </div>
            </div>
            <button className="edit-btn" title={t('scheduling.editAssignments')}>
              {t('scheduling.editTeam')}
            </button>
          </div>
          <div className="card-body">
            <TeamRoster
              assignments={setlist.assignments}
              compact
              onMemberClick={
                onAssignmentClick
                  ? (assignmentId) => onAssignmentClick(setlist.id, assignmentId)
                  : undefined
              }
            />
          </div>
        </div>
      ))}
    </div>
  );
}
