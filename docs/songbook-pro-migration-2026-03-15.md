# SongBook Pro → Javya Migration Guide

Date: 2026-03-15

---

## Overview

This document describes how to export an existing song library from SongBook Pro and import it into Javya. The ChordPro ZIP export is the recommended path since SongBook Pro stores songs internally as ChordPro — no conversion needed.

---

## Step 1: Export from SongBook Pro

### Option A — ChordPro ZIP (recommended)

1. Open SongBook Pro on your phone/tablet
2. Select all songs (or the ones you want to migrate)
3. Tap **Share** → choose **ChordPro** as the export format
4. When exporting multiple songs, SongBook Pro automatically creates a **ZIP archive**
5. Save/send the ZIP to your computer (AirDrop, email, or save to Files)

### Option B — Backup file

1. Go to **Settings → Backup & Sync → Backup Library**
2. This creates a `.sbpbackup` file (which is a ZIP internally)
3. Rename `.sbpbackup` → `.zip` and extract
4. The ChordPro files inside can be re-zipped for import into Javya

### Option C — Individual songs

1. Open a song in SongBook Pro
2. Tap **Share** → choose **ChordPro**
3. Save/send the `.cho` file
4. Repeat per song (only practical for small libraries)

---

## Step 2: Import into Javya

1. Open Javya → **Songs** page → **Import** button
2. Choose **File upload** and select the ZIP archive (or individual `.cho` files)
3. Javya automatically:
   - Extracts all `.cho`/`.chordpro` files from the ZIP (up to 1,000 songs)
   - Parses ChordPro metadata: title, artist, key, tempo, capo
   - Detects key from chord progressions if not specified in metadata
   - Checks for duplicates against existing songs in the database
4. **Preview** — review parsed songs, edit metadata if needed, select/deselect songs
5. **Confirm** — import selected songs (choose Create, Merge, or Skip per song)

---

## Metadata Mapping

| SongBook Pro Field | ChordPro Directive | Javya Field |
|---|---|---|
| Title | `{title}` / `{t}` | `name` |
| Artist | `{artist}` | `artist` |
| Composer | `{composer}` | stored in `notes` |
| Key | `{key}` | `original_key` |
| Tempo | `{tempo}` | `tempo_bpm` |
| Capo | `{capo}` | stored in `notes` |
| Time signature | `{time}` | not mapped |
| Copyright | `{copyright}` | not mapped |
| CCLI | `{ccli}` | not mapped |
| Lyrics + Chords | `[G]Amazing [D7]grace` | `chordpro_chart` + `lyrics` |
| Section markers | `{start_of_verse}` etc. | preserved in `chordpro_chart` |

---

## What Transfers

- Song titles, artists, keys, tempo
- Full chord charts with inline chords
- Section markers (verse, chorus, bridge, etc.)
- Lyrics (extracted separately from chord chart)

## What Won't Transfer

- **Setlists** — SongBook Pro sets are not included in ChordPro export; recreate in Javya
- **Folders/tags** — SongBook Pro organizational structure is not in ChordPro format
- **Custom formatting** — font sizes, colors, layout preferences
- **PDF annotations** — any markups on PDF versions

---

## Import Limits

| Item | Limit |
|------|-------|
| Files per upload | 20 (use ZIP for larger libraries) |
| Individual file size | 1 MB |
| ZIP archive size | 200 MB |
| Files in ZIP | 1,000 |
| Pasted text | 50 KB |
| URL fetch | 1 MB, 10s timeout |

---

## Alternative Import Methods

Javya also supports importing songs via:
- **Clipboard paste** — paste ChordPro text directly
- **URL fetch** — provide a URL to a ChordPro file online
- **Other formats** — OpenLyrics, OpenSong, OnSong, Ultimate Guitar, plain text

---

## Troubleshooting

- **Encoding issues**: SongBook Pro exports UTF-8 by default. Javya handles UTF-8, Mac Roman, CP1252, and Latin-1 automatically.
- **Missing metadata**: If songs lack `{title}` directives, Javya falls back to the filename as the song name.
- **Duplicate detection**: Javya checks name + artist against existing songs and warns during preview. Choose Merge to update or Skip to ignore.
- **`.sbpbackup` won't open**: Rename to `.zip` first. Use [SongBook Pro Database Examiner](https://stevesmusictools.com/sbp/) to inspect contents if needed.

---

## References

- [SongBook Pro — Backup & Sync](https://songbook-pro.com/docs/manual/settings/backup-sync/)
- [SongBook Pro — Sharing Songs](https://songbook-pro.com/docs/getting-started/deleting-and-sharing/)
- [SongBook Pro — ChordPro Syntax](https://songbook-pro.com/docs/manual/chordpro/)
- [SongBook Pro Database Examiner](https://stevesmusictools.com/sbp/)
