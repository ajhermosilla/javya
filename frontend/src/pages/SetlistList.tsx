import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSetlists } from '../hooks/useSetlists';
import { SetlistCard } from '../components/SetlistCard';
import { SetlistForm } from '../components/SetlistForm';
import { setlistsApi } from '../api/setlists';
import type { Setlist, SetlistCreate } from '../types/setlist';
import './SetlistList.css';

type View = 'list' | 'create' | 'edit';

export function SetlistList() {
  const { t } = useTranslation();
  const [view, setView] = useState<View>('list');
  const [editingSetlist, setEditingSetlist] = useState<Setlist | undefined>();

  const { setlists, loading, error, refetch } = useSetlists();

  const handleCreate = async (data: SetlistCreate) => {
    await setlistsApi.create(data);
    setView('list');
    refetch();
  };

  const handleUpdate = async (data: SetlistCreate) => {
    if (editingSetlist) {
      await setlistsApi.update(editingSetlist.id, data);
      setView('list');
      setEditingSetlist(undefined);
      refetch();
    }
  };

  const handleEdit = (setlist: Setlist) => {
    setEditingSetlist(setlist);
    setView('edit');
  };

  const handleCancel = () => {
    setView('list');
    setEditingSetlist(undefined);
  };

  if (view === 'create') {
    return (
      <div className="setlist-list-page">
        <SetlistForm onSubmit={handleCreate} onCancel={handleCancel} />
      </div>
    );
  }

  if (view === 'edit' && editingSetlist) {
    return (
      <div className="setlist-list-page">
        <SetlistForm
          setlist={editingSetlist}
          onSubmit={handleUpdate}
          onCancel={handleCancel}
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
    <div className="setlist-list-page">
      <header className="page-header">
        <h1>{t('setlists.title')}</h1>
        <button className="add-button" onClick={() => setView('create')}>
          {t('setlists.addSetlist')}
        </button>
      </header>

      {loading ? (
        <div className="loading">{t('common.loading')}</div>
      ) : setlists.length === 0 ? (
        <div className="no-results">{t('setlists.noResults')}</div>
      ) : (
        <div className="setlists-grid">
          {setlists.map(setlist => (
            <SetlistCard
              key={setlist.id}
              setlist={setlist}
              onClick={() => handleEdit(setlist)}
              onEdit={() => handleEdit(setlist)}
              onDelete={refetch}
            />
          ))}
        </div>
      )}
    </div>
  );
}
