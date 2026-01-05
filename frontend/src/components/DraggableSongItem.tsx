import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useTranslation } from 'react-i18next';
import type { SetlistSong } from '../types/setlist';
import './DraggableSongItem.css';

interface DraggableSongItemProps {
  item: SetlistSong;
  onRemove: () => void;
}

export function DraggableSongItem({ item, onRemove }: DraggableSongItemProps) {
  const { t } = useTranslation();
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`draggable-song-item ${isDragging ? 'dragging' : ''}`}
    >
      <div className="drag-handle" {...attributes} {...listeners}>
        <span className="drag-icon">⋮⋮</span>
      </div>

      <div className="song-info">
        <span className="song-position">{item.position + 1}</span>
        <div className="song-details">
          <span className="song-name">{item.song?.name ?? t('common.error')}</span>
          {item.song?.artist && (
            <span className="song-artist">{item.song.artist}</span>
          )}
        </div>
        {item.song?.original_key && (
          <span className="song-key">{t(`keys.${item.song.original_key}`)}</span>
        )}
      </div>

      <button className="remove-button" onClick={onRemove} aria-label="Remove">
        ×
      </button>
    </div>
  );
}
