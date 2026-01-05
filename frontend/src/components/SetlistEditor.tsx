import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { useSetlist } from '../hooks/useSetlist';
import { setlistsApi } from '../api/setlists';
import { SongPicker } from './SongPicker';
import { DraggableSongItem } from './DraggableSongItem';
import type { SetlistSong, SetlistSongCreate } from '../types/setlist';
import type { Song } from '../types/song';
import './SetlistEditor.css';

type ExportFormat = 'freeshow';

interface SetlistEditorProps {
  setlistId: string;
  onBack: () => void;
}

export function SetlistEditor({ setlistId, onBack }: SetlistEditorProps) {
  const { t } = useTranslation();
  const { setlist, loading, refetch } = useSetlist(setlistId);
  const [songs, setSongs] = useState<SetlistSong[]>([]);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    if (setlist?.songs) {
      setSongs(setlist.songs);
      setHasChanges(false);
    }
  }, [setlist]);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setSongs((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id);
        const newIndex = items.findIndex((i) => i.id === over.id);
        const newItems = arrayMove(items, oldIndex, newIndex);
        // Update positions
        return newItems.map((item, idx) => ({ ...item, position: idx }));
      });
      setHasChanges(true);
    }
  };

  const handleAddSong = (song: Song) => {
    const newSetlistSong: SetlistSong = {
      id: `temp-${Date.now()}`,
      song_id: song.id,
      position: songs.length,
      notes: null,
      song: song,
    };
    setSongs([...songs, newSetlistSong]);
    setHasChanges(true);
  };

  const handleRemoveSong = (id: string) => {
    setSongs((items) => {
      const filtered = items.filter((i) => i.id !== id);
      return filtered.map((item, idx) => ({ ...item, position: idx }));
    });
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!setlist) return;

    setSaving(true);
    try {
      const songsData: SetlistSongCreate[] = songs.map((s, idx) => ({
        song_id: s.song_id,
        position: idx,
        notes: s.notes,
      }));

      await setlistsApi.update(setlist.id, {
        name: setlist.name,
        description: setlist.description,
        service_date: setlist.service_date,
        event_type: setlist.event_type,
        songs: songsData,
      });

      await refetch();
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save setlist:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async (format: ExportFormat) => {
    if (!setlist) return;

    setExporting(true);
    try {
      if (format === 'freeshow') {
        await setlistsApi.exportFreeshow(setlist.id, setlist.name);
      }
    } catch (error) {
      console.error('Failed to export setlist:', error);
    } finally {
      setExporting(false);
    }
  };

  if (loading || !setlist) {
    return (
      <div className="setlist-editor">
        <div className="editor-loading">{t('common.loading')}</div>
      </div>
    );
  }

  const excludeIds = songs.map((s) => s.song_id);

  return (
    <div className="setlist-editor">
      <header className="editor-header">
        <div className="editor-header-left">
          <button className="back-button" onClick={onBack}>
            ← {t('common.back')}
          </button>
          <div className="editor-title">
            <h1>{setlist.name}</h1>
            {setlist.service_date && (
              <span className="editor-date">
                {new Date(setlist.service_date).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <div className="editor-header-actions">
          <button
            className="export-button"
            onClick={() => handleExport('freeshow')}
            disabled={exporting || songs.length === 0}
          >
            {exporting ? t('setlistEditor.exporting') : t('setlistEditor.exportFreeshow')}
          </button>
          <button
            className="save-button"
            onClick={handleSave}
            disabled={!hasChanges || saving}
          >
            {saving ? t('form.saving') : t('form.save')}
          </button>
        </div>
      </header>

      <div className="editor-content">
        <div className="editor-songs">
          <h2>{t('setlistEditor.songOrder')}</h2>
          {songs.length === 0 ? (
            <div className="songs-empty">{t('setlistEditor.noSongs')}</div>
          ) : (
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={songs.map((s) => s.id)}
                strategy={verticalListSortingStrategy}
              >
                {songs.map((item) => (
                  <DraggableSongItem
                    key={item.id}
                    item={item}
                    onRemove={() => handleRemoveSong(item.id)}
                  />
                ))}
              </SortableContext>
            </DndContext>
          )}
        </div>

        <div className="editor-picker">
          <SongPicker excludeIds={excludeIds} onSelect={handleAddSong} />
        </div>
      </div>
    </div>
  );
}
