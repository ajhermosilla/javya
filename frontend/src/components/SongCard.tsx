import { useTranslation } from 'react-i18next';
import type { Song } from '../types/song';
import { songsApi } from '../api/songs';
import './SongCard.css';

interface SongCardProps {
  song: Song;
  onClick: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

export function SongCard({ song, onClick, onEdit, onDelete }: SongCardProps) {
  const { t } = useTranslation();

  const handleDelete = async () => {
    if (window.confirm(t('songs.confirmDelete'))) {
      try {
        await songsApi.delete(song.id);
        onDelete();
      } catch (error) {
        console.error('Failed to delete song:', error);
      }
    }
  };

  return (
    <div className="song-card">
      <div className="song-card-header" onClick={onClick} role="button" tabIndex={0}>
        <h3 className="song-name">{song.name}</h3>
        {song.artist && <p className="song-artist">{song.artist}</p>}
      </div>

      <div className="song-card-details">
        {song.original_key && (
          <span className="tag key-tag">
            {t(`keys.${song.original_key}`)}
          </span>
        )}
        {song.mood && (
          <span className="tag mood-tag">
            {t(`moods.${song.mood}`)}
          </span>
        )}
        {song.tempo_bpm && (
          <span className="tag tempo-tag">{song.tempo_bpm} BPM</span>
        )}
      </div>

      {song.themes && song.themes.length > 0 && (
        <div className="song-themes">
          {song.themes.map(theme => (
            <span key={theme} className="theme-tag">
              {t(`themes.${theme}`)}
            </span>
          ))}
        </div>
      )}

      <div className="song-card-actions">
        <button className="edit-button" onClick={onEdit}>
          {t('songs.editSong')}
        </button>
        <button className="delete-button" onClick={handleDelete}>
          {t('songs.deleteSong')}
        </button>
      </div>
    </div>
  );
}
