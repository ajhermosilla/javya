import { useTranslation } from 'react-i18next';
import type { Song } from '../types/song';
import './SongDetail.css';

interface SongDetailProps {
  song: Song;
  onBack: () => void;
  onEdit: () => void;
}

export function SongDetail({ song, onBack, onEdit }: SongDetailProps) {
  const { t } = useTranslation();

  return (
    <div className="song-detail">
      <header className="detail-header">
        <button className="back-button" onClick={onBack}>
          ← {t('common.back')}
        </button>
        <button className="edit-button" onClick={onEdit}>
          {t('songs.editSong')}
        </button>
      </header>

      <div className="detail-content">
        <div className="detail-main">
          <h1 className="song-title">{song.name}</h1>
          {song.artist && <p className="song-artist">{song.artist}</p>}

          <div className="song-meta">
            {song.original_key && (
              <span className="meta-item">
                <span className="meta-label">{t('form.originalKey')}:</span>
                <span className="meta-value">{t(`keys.${song.original_key}`)}</span>
              </span>
            )}
            {song.preferred_key && (
              <span className="meta-item">
                <span className="meta-label">{t('form.preferredKey')}:</span>
                <span className="meta-value">{t(`keys.${song.preferred_key}`)}</span>
              </span>
            )}
            {song.tempo_bpm && (
              <span className="meta-item">
                <span className="meta-label">{t('form.tempo')}:</span>
                <span className="meta-value">{song.tempo_bpm} BPM</span>
              </span>
            )}
            {song.mood && (
              <span className="meta-item">
                <span className="meta-label">{t('form.mood')}:</span>
                <span className="meta-value">{t(`moods.${song.mood}`)}</span>
              </span>
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

          {song.url && (
            <div className="song-url">
              <a href={song.url} target="_blank" rel="noopener noreferrer">
                {t('detail.watchVideo')}
              </a>
            </div>
          )}
        </div>

        {song.chordpro_chart && (
          <section className="detail-section">
            <h2>{t('form.chordproChart')}</h2>
            <pre className="chordpro-content">{song.chordpro_chart}</pre>
          </section>
        )}

        {song.lyrics && (
          <section className="detail-section">
            <h2>{t('form.lyrics')}</h2>
            <pre className="lyrics-content">{song.lyrics}</pre>
          </section>
        )}

        {song.min_band && song.min_band.length > 0 && (
          <section className="detail-section">
            <h2>{t('form.minBand')}</h2>
            <div className="min-band-list">
              {song.min_band.map((member, i) => (
                <span key={i} className="band-member">{member}</span>
              ))}
            </div>
          </section>
        )}

        {song.notes && (
          <section className="detail-section">
            <h2>{t('form.notes')}</h2>
            <p className="notes-content">{song.notes}</p>
          </section>
        )}
      </div>
    </div>
  );
}
