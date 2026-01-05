import { useTranslation } from 'react-i18next';
import type { Setlist } from '../types/setlist';
import { setlistsApi } from '../api/setlists';
import './SetlistCard.css';

interface SetlistCardProps {
  setlist: Setlist;
  onClick: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

export function SetlistCard({ setlist, onClick, onEdit, onDelete }: SetlistCardProps) {
  const { t } = useTranslation();

  const handleDelete = async () => {
    if (window.confirm(t('setlists.confirmDelete'))) {
      try {
        await setlistsApi.delete(setlist.id);
        onDelete();
      } catch (error) {
        console.error('Failed to delete setlist:', error);
      }
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString();
  };

  const songCount = setlist.song_count;

  return (
    <div className="setlist-card">
      <div className="setlist-card-header" onClick={onClick} role="button" tabIndex={0}>
        <h3 className="setlist-name">{setlist.name}</h3>
        {setlist.service_date && (
          <p className="setlist-date">{formatDate(setlist.service_date)}</p>
        )}
      </div>

      <div className="setlist-card-details">
        {setlist.event_type && (
          <span className="tag event-tag">
            {t(`eventTypes.${setlist.event_type}`)}
          </span>
        )}
        <span className="tag song-count-tag">
          {songCount} {songCount === 1 ? 'song' : 'songs'}
        </span>
      </div>

      {setlist.description && (
        <p className="setlist-description">{setlist.description}</p>
      )}

      <div className="setlist-card-actions">
        <button className="edit-button" onClick={onEdit}>
          {t('setlists.editSetlist')}
        </button>
        <button className="delete-button" onClick={handleDelete}>
          {t('setlists.deleteSetlist')}
        </button>
      </div>
    </div>
  );
}
