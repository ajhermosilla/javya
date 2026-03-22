# Code Review — 2026-03-22

Full codebase review of backend, frontend, tests, documentation, and configuration.

---

## Critical — Fix this week

### 1. SSRF vulnerability in URL import endpoint
- **File:** `backend/app/routers/import_songs.py:255-284`
- `preview_url_import` fetches arbitrary URLs with no restrictions. No private IP blocking, no scheme validation.
- Attacker can probe internal services (`http://db:5432`, `http://169.254.169.254/`).
- **Impact:** Internal network reconnaissance, potential data exfiltration.

### 2. Default SECRET_KEY is a hardcoded placeholder
- **File:** `backend/app/config.py:12`, `docker-compose.yml:34`
- `secret_key: str = "generate_a_random_secret_key_here"` — dev compose uses this as default.
- Anyone running `docker compose up` without setting `SECRET_KEY` has forged-token vulnerability.
- **Impact:** JWT token forgery in dev environments.

### 3. CLAUDE.md documents wrong env var for JWT secret
- **File:** `CLAUDE.md:241`
- Documents `JWT_SECRET_KEY` but the actual env var is `SECRET_KEY` (from `config.py`).
- A developer setting `JWT_SECRET_KEY` silently gets the insecure default.
- **Impact:** Misleading docs lead to insecure deployments.

### 4. CLAUDE.md documents wrong import endpoint prefix
- **File:** `CLAUDE.md:115`, `backend/app/main.py:49`
- Docs say `/api/v1/import/preview` but actual is `/api/v1/songs/import/preview`.
- **Impact:** Broken API calls for developers following the docs.

---

## High — Fix this week

### 5. Frontend import API bypasses shared client
- **File:** `frontend/src/api/import.ts:14-101`
- Uses raw `fetch()` — no timeout (30s in client.ts not applied), no 401 redirect.
- **Impact:** Hung requests on slow uploads, no auth expiry handling.

### 6. Frontend auth API bypasses shared client
- **File:** `frontend/src/api/auth.ts:6-50`
- Same raw `fetch()` issue — no timeout protection on login/register.
- **Impact:** Infinite spinner on network issues.

### 7. Race condition in data hooks
- **Files:** `frontend/src/hooks/useSongs.ts:17-29`, `useSetlists.ts`, `useSetlist.ts`, `useAvailability.ts`, `useScheduling.ts`
- No cancellation of in-flight requests. Fast filter changes can show stale results.
- **Impact:** UI shows wrong data after rapid search/filter changes.

### 8. Delete/edit buttons shown to all users
- **Files:** `frontend/src/components/SongCard.tsx:63-68`, `SetlistCard.tsx:59-65`
- Buttons visible regardless of role. Members click "Delete" and get a confusing `alert()` error.
- **Impact:** Poor UX for member-role users.

### 9. Broken navigation in SchedulingPage
- **File:** `frontend/src/pages/SchedulingPage.tsx:109`
- Uses `navigate('/setlists/${id}')` but app uses state-based tabs, not React Router routes.
- **Impact:** Dead-end navigation for non-admin users clicking a setlist.

### 10. No upper bound on BulkAvailabilityCreate
- **File:** `backend/app/schemas/availability.py:110`
- `entries: list[AvailabilityCreate]` has no `max_length`. Thousands of entries = DoS.
- **Impact:** Server resource exhaustion via single request.

### 11. Unmaintained auth packages
- **File:** `backend/requirements.txt:16-17`
- `python-jose` unmaintained since 2022, `passlib` since 2020.
- **Impact:** No security patches, potential compatibility issues.

### 12. CLAUDE.md test count and architecture are stale
- **File:** `CLAUDE.md:27,153-166`
- Test count says 369 but actual is 373. Architecture tree missing `rate_limit.py`, `middleware.py`, `templates/`. Models list missing `SetlistSong`, `AvailabilityPattern`.
- **Impact:** Misleading documentation for contributors and AI tools.

### 13. Dev docker-compose.yml deprecated version key
- **File:** `docker-compose.yml:4`
- `version: '3.8'` — generates deprecation warning. Already removed from prod compose.
- **Impact:** Console noise, inconsistency with prod.

---

## Medium — Fix during the cycle

### 14. Hardcoded English strings in frontend
- **Files:** `SetlistCard.tsx:51`, `ErrorBoundary.tsx:42`, `Sidebar.tsx:26`, `DraggableSongItem.tsx:51`, `LanguageSwitcher.tsx:24`
- Multiple strings bypass the i18n system. Won't translate when language is switched.

### 15. SetlistCard missing keyboard handler
- **File:** `frontend/src/components/SetlistCard.tsx:37`
- Has `role="button"` and `tabIndex={0}` but no `onKeyDown`. SongCard has this fixed already.

### 16. `formatLocalDate` duplicated in 4 files
- **Files:** `AvailabilityPage.tsx:9`, `SchedulingPage.tsx:17`, `AvailabilityCalendar.tsx:6`, `ScheduleCalendar.tsx:6`
- Same function copy-pasted. Should be a shared utility.

### 17. No unsaved-changes warning in SetlistEditor
- **File:** `frontend/src/components/SetlistEditor.tsx`
- Clicking "Back" silently discards changes when `hasChanges` is true.

### 18. SongPicker fires API on every keystroke
- **File:** `frontend/src/components/SongPicker.tsx:15`
- No debounce on search input — triggers API call per character.

### 19. Pattern delete has no confirmation
- **File:** `frontend/src/components/PatternEditor.tsx:87`
- Unlike song/setlist delete which use `window.confirm`, pattern delete is immediate.

### 20. Eager loading on list views
- **File:** `backend/app/models/setlist.py:38-50`
- `lazy="selectin"` on `songs` and `assignments` means list endpoints load all related data.

### 21. Cannot clear nullable fields via update
- **Files:** `backend/app/routers/availability.py:282-296`, `setlists.py:550-555`
- `if field is not None` pattern means `None` = "no change", so fields can never be cleared.

### 22. CONTRIBUTING.md references black/isort
- **File:** `CONTRIBUTING.md:84-91`
- Neither `black` nor `isort` are in requirements.txt. Contributors get `command not found`.

### 23. README.md stale architecture and incomplete import list
- **File:** `README.md:34,98-101`
- Missing OnSong, Ultimate Guitar, URL, clipboard, ZIP from import list. Models and routers lists incomplete.

### 24. .env.example missing variables
- **File:** `.env.example`
- Missing `TEST_DATABASE_URL`, `FRONTEND_PORT`, `RATE_LIMIT_ENABLED`.

### 25. VITE_DEFAULT_LANGUAGE defined but never used
- **File:** `.env.example:31`
- No code references this env var. Dead configuration.

---

## Low — Track but don't block on

- Missing `aria-label` on SearchBar, FilterBar, SongPicker inputs
- ScheduleCalendar day cells not keyboard-accessible (no role/tabIndex/onKeyDown)
- `useDebounce` hook exists but unused (dead code)
- `DAY_NAMES` constant exported but unused (dead code)
- Missing DB indexes on `songs.artist` and `setlist_songs.song_id`
- FastAPI app `version: "0.1.0"` should be 0.7
- Registration race condition for first admin (acknowledged in code comment)
- `frontend/package.json` name "frontend" → "javya", version "0.0.0" → "0.7.0"
- `frontend/package.json`: dev Dockerfile uses `npm install` instead of `npm ci`
- No `.dockerignore` — `COPY . .` includes tests, __pycache__, .env in prod image
- Duplicate `KEYS` constant defined in 3 frontend files

---

## Fix Summary

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| 1 | Critical | SSRF in URL import | Fixed |
| 2 | Critical | Hardcoded default SECRET_KEY | Fixed |
| 3 | Critical | CLAUDE.md wrong JWT env var name | Fixed |
| 4 | Critical | CLAUDE.md wrong import endpoint prefix | Fixed |
| 5 | High | Import API bypasses shared client | |
| 6 | High | Auth API bypasses shared client | |
| 7 | High | Race condition in data hooks | |
| 8 | High | Delete/edit buttons shown to all users | |
| 9 | High | Broken navigation in SchedulingPage | |
| 10 | High | No upper bound on bulk availability | |
| 11 | High | Unmaintained auth packages | |
| 12 | High | CLAUDE.md stale test count and architecture | |
| 13 | High | Dev compose deprecated version key | |
| 14 | Medium | Hardcoded English strings | |
| 15 | Medium | SetlistCard missing keyboard handler | |
| 16 | Medium | formatLocalDate duplicated 4x | |
| 17 | Medium | No unsaved-changes warning | |
| 18 | Medium | SongPicker no debounce | |
| 19 | Medium | Pattern delete no confirmation | |
| 20 | Medium | Eager loading on list views | |
| 21 | Medium | Cannot clear nullable fields | |
| 22 | Medium | CONTRIBUTING.md references missing tools | |
| 23 | Medium | README.md stale architecture | |
| 24 | Medium | .env.example missing variables | |
| 25 | Medium | Dead VITE_DEFAULT_LANGUAGE config | |
