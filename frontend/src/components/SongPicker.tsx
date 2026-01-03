import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSongs } from '../hooks/useSongs';
import type { Song } from '../types/song';
import './SongPicker.css';

interface SongPickerProps {
  excludeIds: string[];
  onSelect: (song: Song) => void;
}

export function SongPicker({ excludeIds, onSelect }: SongPickerProps) {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const { songs, loading } = useSongs({ search: search || undefined });

  const availableSongs = songs.filter(song => !excludeIds.includes(song.id));

  return (
    <div className="song-picker">
      <div className="picker-header">
        <h3>{t('setlistEditor.addSongs')}</h3>
        <input
          type="text"
          className="picker-search"
          placeholder={t('songs.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="picker-list">
        {loading ? (
          <div className="picker-loading">{t('common.loading')}</div>
        ) : availableSongs.length === 0 ? (
          <div className="picker-empty">
            {search ? t('songs.noResults') : t('setlistEditor.allSongsAdded')}
          </div>
        ) : (
          availableSongs.map(song => (
            <button
              key={song.id}
              className="picker-item"
              onClick={() => onSelect(song)}
            >
              <div className="picker-item-info">
                <span className="picker-item-name">{song.name}</span>
                {song.artist && (
                  <span className="picker-item-artist">{song.artist}</span>
                )}
              </div>
              <span className="picker-item-add">+</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
