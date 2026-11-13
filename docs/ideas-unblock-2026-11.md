# Ideas to Unblock Javya (Nov 2026)

Javya has been idle since March 2026. Meanwhile the ICER worship schedule for November 2026 was built
by hand from three separate files (last month's `.docx`, a song-statistics `.ods`, and a Google Form
CSV) and published as a PDF. That manual run is the clearest spec of what Javya has to replace.

These ideas aim to make Javya useful **to one leader, on cheap hardware, before the whole team adopts it**.

---

## 0. Guiding idea: single-leader value first

Adoption is stalled partly because Javya only pays off once everyone has an account. Flip that:

- The worship leader uses Javya alone to produce what the team already consumes: the monthly PDF,
  chord charts and slides.
- The team keeps receiving a PDF/link (e.g. the group's Google Drive) and doesn't need an account.
- Accounts, confirmations and notifications come later, once the outputs have proven themselves.

---

## 1. Minimal, cheap hardware

Javya should run on hardware a small church can afford or already owns, with no internet required on Sunday.

**Server options (pick one):**

| Option | Approx. cost | Notes |
|--------|--------------|-------|
| Existing NAS (Docker) | $0 | Already on the roadmap ("Deploy to NAS") |
| Raspberry Pi 4/5 (4 GB) + SSD | ~US$ 80–120 | Low power, can live in the sound booth |
| Used mini PC (Intel N100 / old NUC) | ~US$ 100–150 | x86, more headroom than a Pi |
| Old laptop | $0 | Built-in battery works as a UPS |

**To investigate:**
- Measure the real footprint (Postgres + FastAPI + static frontend). Target: under 1 GB RAM total and an ARM64 image.
- Decide whether to offer **SQLite as an option** for one-box installs. Today the models use
  Postgres `ARRAY` columns (`themes`, `min_band`), so this needs an abstraction or JSON columns.
- Offline LAN mode: the church Wi-Fi router serves Javya at a local name (`javya.local` via mDNS).
  Phones and the projection PC connect without internet.
- Backups: a nightly DB dump plus ChordPro export to a USB drive or cloud folder.
- Clients are already covered in [`minimal-clients.md`](minimal-clients.md) (old Android phones, Chromebooks).

---

## 2. ChordPro as the single source of truth for songs

Today `Song` stores **both** `lyrics` and `chordpro_chart`, so the same content lives twice and can drift.

- Make `chordpro_chart` canonical. Derive plain lyrics (for slides) and chord charts (for musicians) from it.
- Use ChordPro directives for metadata: `{title}`, `{artist}`, `{key}`, `{tempo}`, and
  `{comment}`/`{start_of_verse}`… for sections. Sections are what drive slide breaks (see §3).
- Allow a **song library as a folder of `.cho` files** that can be imported/exported in bulk and kept
  in git or a shared drive. The SongBook Pro migration already produces ChordPro ZIPs.
- Keep the per-song reference video (`url` field). For ICER, every song in the monthly PDF links to a
  specific YouTube video, so link verification (oEmbed) could be automated.
- Import song **usage history** from the existing statistics sheet ("Estadística de Canciones desde
  Mar-25": date, song, version, key, type fast/slow). That bootstraps the "Song usage stats" feature
  (v0.9) with 1.5 years of real data.

---

## 3. Slides generated from the songs

FreeShow and Quelea exports exist, but they depend on that software being installed and configured.
Javya can produce slides itself:

- **Browser projection view:** fullscreen, black background, large text, keyboard/clicker navigation,
  works on a second screen. Any laptop connected to the projector can run it with no extra software.
- **Slide splitting from ChordPro:** one slide per section, max N lines per slide, chords stripped.
  Repeated choruses are reused.
- **Export to PDF** (one slide per page, 16:9) and optionally `.pptx` for churches that use PowerPoint/Keynote.
- **Optional "stage view"** for musicians: the same setlist with chords and the current key, on a phone or tablet.

---

## 4. Outputs that mirror what the team already uses

From the November 2026 ICER run:

- **Monthly schedule export** (R-0102 "Calendario de Asistencia Mensual") as PDF/DOCX. One block per
  Sunday: songs with links, version, key, roster by role, and who leads. Blocks never split across
  pages, and there is a clear separator between dates.
- **Import availability from a Google Form CSV** ("R-0101"), with name aliases (a nickname in the form →
  the member's full name), so the existing form keeps working while Javya does the matching.
- **Roster conventions as data:** primary/backup per role (e.g. primary sound tech plus a backup),
  combined roles ("Bajo y Sonido", "Voz princ. y Guit. Eléc."), omitting absent instruments, and
  showing vacant fixed roles as blanks.
- **Validation before publishing:** flag anyone assigned on a date they marked unavailable, list
  available-but-unassigned members, and skip Sundays that have already passed.
- **"As happened" edits:** after a Sunday, record the actual lineup, which differs from the plan.

---

## Suggested order

1. Unblock the base: merge PR #27 (fix the failing backend tests) and deploy on the NAS.
2. ChordPro canonical (§2) plus importing the ICER song library and history.
3. Browser projection view (§3). It gives visible Sunday value with no accounts needed.
4. Monthly schedule export and form-CSV import (§4), so the next ICER schedule comes out of Javya.
5. Hardware footprint measurement and SQLite decision (§1).
