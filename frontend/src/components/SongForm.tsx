import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Song, SongCreate, MusicalKey, Mood, Theme } from '../types/song';
import { songsApi, type ExistingSongSummary } from '../api/songs';
import { DuplicateWarning } from './DuplicateWarning';
import './SongForm.css';

// Keys ordered by Circle of Fifths: sharp keys clockwise, flat keys counter-clockwise
const KEYS: MusicalKey[] = [
  'C', 'G', 'D', 'A', 'E', 'B', 'F#',  // Sharp keys
  'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb',   // Flat keys
];
const MOODS: Mood[] = ['Joyful', 'Reflective', 'Triumphant', 'Intimate', 'Peaceful', 'Energetic', 'Hopeful', 'Solemn', 'Celebratory'];
const THEMES: Theme[] = ['Worship', 'Communion', 'Offering', 'Opening', 'Closing', 'Prayer', 'Declaration', 'Thanksgiving', 'Faith', 'Grace', 'Salvation', 'Baptism', 'Christmas', 'Holy Week'];

interface SongFormProps {
  song?: Song;
  onSubmit: (data: SongCreate) => Promise<void>;
  onCancel: () => void;
  onNavigateToSong?: (id: string) => void;
}

export function SongForm({ song, onSubmit, onCancel, onNavigateToSong }: SongFormProps) {
  const { t } = useTranslation();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [duplicateMatch, setDuplicateMatch] = useState<ExistingSongSummary | null>(null);
  const [pendingData, setPendingData] = useState<SongCreate | null>(null);

  const [name, setName] = useState(song?.name || '');
  const [artist, setArtist] = useState(song?.artist || '');
  const [url, setUrl] = useState(song?.url || '');
  const [originalKey, setOriginalKey] = useState<MusicalKey | ''>(song?.original_key || '');
  const [preferredKey, setPreferredKey] = useState<MusicalKey | ''>(song?.preferred_key || '');
  const [tempoBpm, setTempoBpm] = useState(song?.tempo_bpm?.toString() || '');
  const [mood, setMood] = useState<Mood | ''>(song?.mood || '');
  const [themes, setThemes] = useState<Theme[]>(song?.themes || []);
  const [lyrics, setLyrics] = useState(song?.lyrics || '');
  const [chordproChart, setChordproChart] = useState(song?.chordpro_chart || '');
  const [minBand, setMinBand] = useState(song?.min_band?.join(', ') || '');
  const [notes, setNotes] = useState(song?.notes || '');

  const handleThemeToggle = (theme: Theme) => {
    setThemes(prev =>
      prev.includes(theme)
        ? prev.filter(t => t !== theme)
        : [...prev, theme]
    );
  };

  const buildSongData = (): SongCreate => ({
    name,
    artist: artist || null,
    url: url || null,
    original_key: originalKey || null,
    preferred_key: preferredKey || null,
    tempo_bpm: tempoBpm ? parseInt(tempoBpm, 10) : null,
    mood: mood || null,
    themes: themes.length > 0 ? themes : null,
    lyrics: lyrics || null,
    chordpro_chart: chordproChart || null,
    min_band: minBand ? minBand.split(',').map(s => s.trim()).filter(Boolean) : null,
    notes: notes || null,
  });

  const submitSong = async (data: SongCreate) => {
    try {
      await onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save song');
      setSaving(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    const data = buildSongData();

    // Only check for duplicates when creating a new song (not editing)
    if (!song) {
      try {
        const response = await songsApi.checkDuplicates([{ name: data.name, artist: data.artist ?? null }]);
        if (response.duplicates.length > 0) {
          // Duplicate found - show warning modal
          setDuplicateMatch(response.duplicates[0].existing_song);
          setPendingData(data);
          setSaving(false);
          return;
        }
      } catch {
        // If duplicate check fails, proceed with creation
      }
    }

    await submitSong(data);
  };

  const handleUseExisting = () => {
    if (duplicateMatch && onNavigateToSong) {
      onNavigateToSong(duplicateMatch.id);
    }
    setDuplicateMatch(null);
    setPendingData(null);
  };

  const handleCreateAnyway = async () => {
    if (pendingData) {
      setSaving(true);
      setDuplicateMatch(null);
      await submitSong(pendingData);
      setPendingData(null);
    }
  };

  const handleCancelDuplicate = () => {
    setDuplicateMatch(null);
    setPendingData(null);
  };

  return (
    <form className="song-form" onSubmit={handleSubmit}>
      <h2>{song ? t('songs.editSong') : t('songs.addSong')}</h2>

      {error && <div className="form-error">{error}</div>}

      <div className="form-group">
        <label htmlFor="name">
          {t('form.name')} <span className="required">*</span>
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="artist">{t('form.artist')}</label>
          <input
            id="artist"
            type="text"
            value={artist}
            onChange={(e) => setArtist(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="url">{t('form.url')}</label>
          <input
            id="url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/..."
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="originalKey">{t('form.originalKey')}</label>
          <select
            id="originalKey"
            value={originalKey}
            onChange={(e) => setOriginalKey(e.target.value as MusicalKey | '')}
          >
            <option value="">--</option>
            {KEYS.map(key => (
              <option key={key} value={key}>{t(`keys.${key}`)}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="preferredKey">{t('form.preferredKey')}</label>
          <select
            id="preferredKey"
            value={preferredKey}
            onChange={(e) => setPreferredKey(e.target.value as MusicalKey | '')}
          >
            <option value="">--</option>
            {KEYS.map(key => (
              <option key={key} value={key}>{t(`keys.${key}`)}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="tempo">{t('form.tempo')}</label>
          <input
            id="tempo"
            type="number"
            min="20"
            max="300"
            value={tempoBpm}
            onChange={(e) => setTempoBpm(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="mood">{t('form.mood')}</label>
          <select
            id="mood"
            value={mood}
            onChange={(e) => setMood(e.target.value as Mood | '')}
          >
            <option value="">--</option>
            {MOODS.map(m => (
              <option key={m} value={m}>{t(`moods.${m}`)}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-group">
        <label>{t('form.themes')}</label>
        <div className="theme-chips">
          {THEMES.map(theme => (
            <button
              key={theme}
              type="button"
              className={`theme-chip ${themes.includes(theme) ? 'selected' : ''}`}
              onClick={() => handleThemeToggle(theme)}
            >
              {t(`themes.${theme}`)}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="lyrics">{t('form.lyrics')}</label>
        <textarea
          id="lyrics"
          value={lyrics}
          onChange={(e) => setLyrics(e.target.value)}
          rows={6}
        />
      </div>

      <div className="form-group">
        <label htmlFor="chordpro">{t('form.chordproChart')}</label>
        <textarea
          id="chordpro"
          value={chordproChart}
          onChange={(e) => setChordproChart(e.target.value)}
          rows={6}
          className="monospace"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="minBand">{t('form.minBand')}</label>
          <input
            id="minBand"
            type="text"
            value={minBand}
            onChange={(e) => setMinBand(e.target.value)}
            placeholder="acoustic guitar, vocals, keys"
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="notes">{t('form.notes')}</label>
        <textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
        />
      </div>

      <div className="form-actions">
        <button type="button" className="cancel-button" onClick={onCancel}>
          {t('form.cancel')}
        </button>
        <button type="submit" className="submit-button" disabled={saving}>
          {saving ? t('form.saving') : t('form.save')}
        </button>
      </div>

      {duplicateMatch && (
        <DuplicateWarning
          existingSong={duplicateMatch}
          onUseExisting={handleUseExisting}
          onCreateAnyway={handleCreateAnyway}
          onCancel={handleCancelDuplicate}
        />
      )}
    </form>
  );
}
