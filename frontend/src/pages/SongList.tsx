import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSongs } from '../hooks/useSongs';
import { SongCard } from '../components/SongCard';
import { SongForm } from '../components/SongForm';
import { SearchBar } from '../components/SearchBar';
import { FilterBar } from '../components/FilterBar';
import { SongDetail } from '../components/SongDetail';
import { ImportModal } from '../components/ImportModal';
import { songsApi } from '../api/songs';
import type { Song, SongCreate, SongFilters, MusicalKey, Mood, Theme } from '../types/song';
import './SongList.css';

type View = 'list' | 'detail' | 'create' | 'edit';

export function SongList() {
  const { t } = useTranslation();
  const [view, setView] = useState<View>('list');
  const [selectedSong, setSelectedSong] = useState<Song | undefined>();
  const [editingSong, setEditingSong] = useState<Song | undefined>();
  const [search, setSearch] = useState('');
  const [keyFilter, setKeyFilter] = useState<MusicalKey | undefined>();
  const [moodFilter, setMoodFilter] = useState<Mood | undefined>();
  const [themeFilter, setThemeFilter] = useState<Theme | undefined>();
  const [showImportModal, setShowImportModal] = useState(false);

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

  const handleCreate = async (data: SongCreate) => {
    await songsApi.create(data);
    setView('list');
    refetch();
  };

  const handleUpdate = async (data: SongCreate) => {
    if (editingSong) {
      await songsApi.update(editingSong.id, data);
      setView('list');
      setEditingSong(undefined);
      refetch();
    }
  };

  const handleView = (song: Song) => {
    setSelectedSong(song);
    setView('detail');
  };

  const handleEdit = (song: Song) => {
    setEditingSong(song);
    setView('edit');
  };

  const handleCancel = () => {
    setView('list');
    setSelectedSong(undefined);
    setEditingSong(undefined);
  };

  const handleNavigateToSong = async (songId: string) => {
    try {
      const song = await songsApi.get(songId);
      setSelectedSong(song);
      setView('detail');
    } catch {
      // If we can't fetch the song, just go back to list
      setView('list');
    }
  };

  if (view === 'create') {
    return (
      <div className="song-list-page">
        <SongForm
          onSubmit={handleCreate}
          onCancel={handleCancel}
          onNavigateToSong={handleNavigateToSong}
        />
      </div>
    );
  }

  if (view === 'edit' && editingSong) {
    return (
      <div className="song-list-page">
        <SongForm song={editingSong} onSubmit={handleUpdate} onCancel={handleCancel} />
      </div>
    );
  }

  if (view === 'detail' && selectedSong) {
    return (
      <div className="song-list-page">
        <SongDetail
          song={selectedSong}
          onBack={handleCancel}
          onEdit={() => handleEdit(selectedSong)}
        />
      </div>
    );
  }

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
        <div className="header-actions">
          <button className="import-button" onClick={() => setShowImportModal(true)}>
            {t('songs.importSongs')}
          </button>
          <button className="add-button" onClick={() => setView('create')}>
            {t('songs.addSong')}
          </button>
        </div>
      </header>

      <ImportModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onImportComplete={refetch}
      />

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
            <SongCard
              key={song.id}
              song={song}
              onClick={() => handleView(song)}
              onEdit={() => handleEdit(song)}
              onDelete={refetch}
            />
          ))}
        </div>
      )}
    </div>
  );
}
