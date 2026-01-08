import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { importApi } from '../api/import';
import type { ImportPreviewResponse, ParsedSong } from '../types/import';
import type { SongCreate } from '../types/song';
import { ImportPreview } from './ImportPreview';
import { ImportEditModal } from './ImportEditModal';
import './ImportModal.css';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportComplete: () => void;
}

type Step = 'select' | 'uploading' | 'preview' | 'saving' | 'complete';
type InputMode = 'file' | 'paste' | 'url';

const MAX_FILES = 20;
const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const MAX_ZIP_SIZE = 10 * 1024 * 1024; // 10MB for ZIP archives
const MAX_PASTE_LENGTH = 50000; // 50KB for pasted text

const isZipFile = (file: File): boolean => {
  return file.name.toLowerCase().endsWith('.zip') || file.type === 'application/zip';
};

export function ImportModal({
  isOpen,
  onClose,
  onImportComplete,
}: ImportModalProps) {
  const { t } = useTranslation();
  const [step, setStep] = useState<Step>('select');
  const [inputMode, setInputMode] = useState<InputMode>('file');
  const [files, setFiles] = useState<File[]>([]);
  const [pastedText, setPastedText] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [previewData, setPreviewData] = useState<ImportPreviewResponse | null>(
    null
  );
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(
    new Set()
  );
  const [error, setError] = useState<string | null>(null);
  const [savedCount, setSavedCount] = useState(0);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    addFiles(selectedFiles);
  };

  const addFiles = (newFiles: File[]) => {
    const validFiles = newFiles
      .filter((f) => {
        const maxSize = isZipFile(f) ? MAX_ZIP_SIZE : MAX_FILE_SIZE;
        return f.size <= maxSize;
      })
      .slice(0, MAX_FILES - files.length);

    setFiles((prev) => [...prev, ...validFiles].slice(0, MAX_FILES));
    setError(null);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleUpload = async () => {
    setStep('uploading');
    setError(null);

    try {
      let result: ImportPreviewResponse;

      if (inputMode === 'url') {
        const trimmedUrl = urlInput.trim();
        if (!trimmedUrl) return;
        result = await importApi.previewUrl(trimmedUrl);
      } else if (inputMode === 'paste') {
        const trimmed = pastedText.trim();
        if (!trimmed) return;
        if (trimmed.length > MAX_PASTE_LENGTH) {
          setError(t('import.pasteTooLong'));
          setStep('select');
          return;
        }
        // Convert pasted text to a File object
        const blob = new Blob([trimmed], { type: 'text/plain' });
        const filesToUpload = [new File([blob], 'pasted_song.txt', { type: 'text/plain' })];
        result = await importApi.preview(filesToUpload);
      } else {
        if (files.length === 0) return;
        result = await importApi.preview(files);
      }

      setPreviewData(result);

      // Pre-select all successful parses
      const successIndices = result.songs
        .map((s, i) => (s.success ? i : -1))
        .filter((i) => i >= 0);
      setSelectedIndices(new Set(successIndices));

      setStep('preview');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setStep('select');
    }
  };

  const handleConfirm = async () => {
    if (!previewData) return;

    const songsToSave = previewData.songs
      .filter((_, i) => selectedIndices.has(i))
      .filter((s): s is ParsedSong & { song_data: SongCreate } =>
        Boolean(s.success && s.song_data)
      )
      .map((s) => s.song_data);

    if (songsToSave.length === 0) return;

    setStep('saving');
    setError(null);

    try {
      const result = await importApi.confirm({ songs: songsToSave });
      setSavedCount(result.saved_count);
      setStep('complete');
      onImportComplete();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
      setStep('preview');
    }
  };

  const handleSaveEdit = (updatedSong: SongCreate) => {
    if (editingIndex === null || !previewData) return;

    const updatedSongs = [...previewData.songs];
    updatedSongs[editingIndex] = {
      ...updatedSongs[editingIndex],
      song_data: updatedSong,
    };

    setPreviewData({
      ...previewData,
      songs: updatedSongs,
    });
    setEditingIndex(null);
  };

  const handleClose = () => {
    // Reset state
    setStep('select');
    setInputMode('file');
    setFiles([]);
    setPastedText('');
    setUrlInput('');
    setPreviewData(null);
    setSelectedIndices(new Set());
    setError(null);
    setSavedCount(0);
    setEditingIndex(null);
    onClose();
  };

  const canUpload =
    inputMode === 'file'
      ? files.length > 0
      : inputMode === 'paste'
        ? pastedText.trim().length > 0
        : urlInput.trim().length > 0;

  if (!isOpen) return null;

  return (
    <div className="import-modal-overlay" onClick={handleClose}>
      <div className="import-modal" onClick={(e) => e.stopPropagation()}>
        <header className="import-modal-header">
          <h2>{t('import.title')}</h2>
          <button
            className="import-close-button"
            onClick={handleClose}
            aria-label={t('common.close')}
          >
            &times;
          </button>
        </header>

        {error && <div className="import-error">{error}</div>}

        {step === 'select' && (
          <div className="import-select">
            <div className="import-tabs">
              <button
                className={`import-tab ${inputMode === 'file' ? 'active' : ''}`}
                onClick={() => setInputMode('file')}
              >
                {t('import.tabFile')}
              </button>
              <button
                className={`import-tab ${inputMode === 'paste' ? 'active' : ''}`}
                onClick={() => setInputMode('paste')}
              >
                {t('import.tabPaste')}
              </button>
              <button
                className={`import-tab ${inputMode === 'url' ? 'active' : ''}`}
                onClick={() => setInputMode('url')}
              >
                {t('import.tabUrl')}
              </button>
            </div>

            {inputMode === 'file' && (
              <>
                <div
                  className="import-drop-zone"
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    multiple
                    accept=".cho,.crd,.chopro,.xml,.txt,.onsong,.zip"
                    onChange={handleFileSelect}
                    id="import-file-input"
                    className="import-file-input"
                  />
                  <label htmlFor="import-file-input" className="import-drop-label">
                    <span className="import-drop-icon">📁</span>
                    <span className="import-drop-text">
                      {t('import.dropFiles')}
                    </span>
                    <span className="import-drop-hint">
                      {t('import.supportedFormats')}
                    </span>
                  </label>
                </div>

                {files.length > 0 && (
                  <div className="import-selected-files">
                    <h3>
                      {t('import.selectedFiles', { count: files.length })}
                    </h3>
                    <ul className="import-file-list">
                      {files.map((f, i) => (
                        <li key={i} className="import-file-item">
                          <span className="import-file-name">{f.name}</span>
                          <button
                            className="import-file-remove"
                            onClick={() => removeFile(i)}
                            aria-label={t('common.remove')}
                          >
                            &times;
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}

            {inputMode === 'paste' && (
              <div className="import-paste-container">
                <textarea
                  className="import-paste-textarea"
                  placeholder={t('import.pastePlaceholder')}
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  rows={12}
                />
                <span className="import-paste-hint">
                  {t('import.pasteHint')}
                </span>
              </div>
            )}

            {inputMode === 'url' && (
              <div className="import-url-container">
                <input
                  type="url"
                  className="import-url-input"
                  placeholder={t('import.urlPlaceholder')}
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                />
                <span className="import-url-hint">
                  {t('import.urlHint')}
                </span>
              </div>
            )}

            <div className="import-actions">
              <button className="import-cancel-button" onClick={handleClose}>
                {t('common.cancel')}
              </button>
              <button
                className="import-upload-button"
                onClick={handleUpload}
                disabled={!canUpload}
              >
                {inputMode === 'url'
                  ? t('import.fetch')
                  : inputMode === 'paste'
                    ? t('import.parse')
                    : t('import.upload')}
              </button>
            </div>
          </div>
        )}

        {step === 'uploading' && (
          <div className="import-loading">
            <div className="import-spinner"></div>
            <p>{t('import.uploading')}</p>
          </div>
        )}

        {step === 'preview' && previewData && (
          <>
            <ImportPreview
              data={previewData}
              selectedIndices={selectedIndices}
              onSelectionChange={setSelectedIndices}
              onEditSong={setEditingIndex}
              onConfirm={handleConfirm}
              onBack={() => setStep('select')}
            />
            {editingIndex !== null &&
              previewData.songs[editingIndex]?.song_data && (
                <ImportEditModal
                  song={previewData.songs[editingIndex].song_data!}
                  fileName={previewData.songs[editingIndex].file_name}
                  onSave={handleSaveEdit}
                  onClose={() => setEditingIndex(null)}
                />
              )}
          </>
        )}

        {step === 'saving' && (
          <div className="import-loading">
            <div className="import-spinner"></div>
            <p>{t('import.saving')}</p>
          </div>
        )}

        {step === 'complete' && (
          <div className="import-complete">
            <div className="import-complete-icon">✓</div>
            <p>{t('import.complete', { count: savedCount })}</p>
            <button className="import-done-button" onClick={handleClose}>
              {t('common.close')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
