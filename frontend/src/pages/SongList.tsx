import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSongs } from '../hooks/useSongs';
import { SongCard } from '../components/SongCard';
import { SearchBar } from '../components/SearchBar';
import { FilterBar } from '../components/FilterBar';
import type { SongFilters, MusicalKey, Mood, Theme } from '../types/song';
import './SongList.css';

export function SongList() {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [keyFilter, setKeyFilter] = useState<MusicalKey | undefined>();
  const [moodFilter, setMoodFilter] = useState<Mood | undefined>();
  const [themeFilter, setThemeFilter] = useState<Theme | undefined>();

  const filters: SongFilters = useMemo(() => ({
    search: search || undefined,
    key: keyFilter,
    mood: moodFilter,
    theme: themeFilter,
  }), [search, keyFilter, moodFilter, themeFilter]);

  const { songs, loading, error, refetch } = useSongs(filters);

  const clearFilters = () => {
    setSearch('');
    setKeyFilter(undefined);
    setMoodFilter(undefined);
    setThemeFilter(undefined);
  };

  const hasFilters = search || keyFilter || moodFilter || themeFilter;

  if (error) {
    return (
      <div className="error-container">
        <p>{t('common.error')}: {error}</p>
        <button onClick={refetch}>{t('common.retry')}</button>
      </div>
    );
  }

  return (
    <div className="song-list-page">
      <header className="page-header">
        <h1>{t('songs.title')}</h1>
        <button className="add-button">{t('songs.addSong')}</button>
      </header>

      <div className="filters-section">
        <SearchBar
          value={search}
          onChange={setSearch}
          placeholder={t('songs.searchPlaceholder')}
        />
        <FilterBar
          keyFilter={keyFilter}
          moodFilter={moodFilter}
          themeFilter={themeFilter}
          onKeyChange={setKeyFilter}
          onMoodChange={setMoodFilter}
          onThemeChange={setThemeFilter}
        />
        {hasFilters && (
          <button className="clear-filters" onClick={clearFilters}>
            {t('common.clearFilters')}
          </button>
        )}
      </div>

      {loading ? (
        <div className="loading">{t('common.loading')}</div>
      ) : songs.length === 0 ? (
        <div className="no-results">{t('songs.noResults')}</div>
      ) : (
        <div className="songs-grid">
          {songs.map(song => (
            <SongCard key={song.id} song={song} onDelete={refetch} />
          ))}
        </div>
      )}
    </div>
  );
}
