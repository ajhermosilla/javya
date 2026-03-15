# Code Review — 2026-03-12

Full codebase review of backend, frontend, tests, documentation, and Docker configuration.

---

## Critical — Must fix before users touch it

### 1. No auth on song create/update
- **File:** `backend/app/routers/songs.py:21-44, 115-147`
- `create_song()` and `update_song()` have zero authentication. Anyone can POST/PUT songs without logging in.
- `delete_song()` correctly requires admin/leader (line 153).
- **Impact:** Unauthenticated users can create and modify songs in the database.

### 2. No auth on setlist create/update
- **File:** `backend/app/routers/setlists.py:50-54, 134-138`
- Same pattern as songs. `create_setlist()` and `update_setlist()` are wide open.
- `delete_setlist()` correctly requires admin/leader (line 193). Exports correctly require login (line 213+).
- **Impact:** Unauthenticated users can create and modify setlists.

### 3. Export functions bypass API base URL
- **File:** `frontend/src/api/setlists.ts:45-113`
- All three export functions (`exportFreeshow`, `exportQuelea`, `exportPdf`) use raw `fetch()` with `BASE_PATH = '/api/v1/setlists'` instead of the `api` client which prepends `API_BASE_URL` from `VITE_API_URL`.
- Works in dev (Vite proxy), breaks in production when frontend and backend are on different domains.
- **Impact:** All exports silently fail in production.

### 4. Backend healthcheck uses curl (not installed)
- **File:** `docker-compose.prod.yml:50`
- Healthcheck runs `curl -f http://localhost:8000/health` but `python:3.12-slim` doesn't include curl.
- Was fixed in the homelab NAS deploy (switched to python urllib) but the fix was not backported here.
- **Impact:** Backend container is always reported as "unhealthy".

---

## High — Should fix before real usage

### 5. Calendar date off-by-one in UTC- timezones
- **Files:** `frontend/src/components/AvailabilityCalendar.tsx:51,66`, `frontend/src/components/ScheduleCalendar.tsx:59`
- Both calendars use `date.toISOString().split('T')[0]` which converts to UTC.
- For Paraguay (UTC-4), dates near midnight render as the previous day.
- The page-level `formatLocalDate()` uses local getters correctly, but the calendar components don't.
- **Impact:** Wrong date displayed or wrong date sent to API near midnight.

### 6. PatternEditor has no error handling
- **File:** `frontend/src/components/PatternEditor.tsx:61-77`
- `handleCreate()`, `handleUpdate()`, `handleDelete()` all await API calls without try/catch.
- On failure, promise rejection is unhandled and UI resets as if it succeeded.
- **Impact:** Users see no feedback when operations fail.

### 7. E2E test suite is broken
- **File:** `frontend/test-results/.last-run.json`
- 10 failing tests across songs and setlists specs.
- Needs investigation — could be stale selectors or actual regressions.

### 8. HTML title says "frontend"
- **File:** `frontend/index.html:7`
- `<title>frontend</title>` — users see this in their browser tab.

---

## Medium — Fix during the cycle

### 9. CONTRIBUTING.md wrong port
- **File:** `CONTRIBUTING.md:55`
- Says `http://localhost:3000`, actual is `http://localhost:5173`.

### 10. README.md lists transposition as "Coming Soon"
- **File:** `README.md:39-44`
- Song transposition has been done since v0.6. The "Coming Soon" list is stale.

### 11. .env.example has blank VITE_API_URL
- **File:** `.env.example:28`
- No default or comment explaining that empty = use Vite proxy (dev only).

### 12. Deprecated `version: '3.8'` in docker-compose.prod.yml
- **File:** `docker-compose.prod.yml:11`
- Compose V2 ignores this field. Not harmful but generates warnings.

### 13. SongCard missing keyboard handler
- **File:** `frontend/src/components/SongCard.tsx:30`
- Has `role="button" tabIndex={0}` but no `onKeyDown` for Enter/Space.
- Accessibility issue for keyboard-only users.

### 14. Containers run as root
- **Files:** `backend/Dockerfile`, `frontend/Dockerfile.prod`
- Both lack a `USER` directive. Low risk behind Traefik but worth hardening.

---

## Low — Track but don't block on

- ~~`sanitize_filename()` doesn't handle quotes in Content-Disposition headers~~ — Fixed: allows apostrophes, escapes quotes
- ~~No rate limiting on auth endpoints~~ — Fixed: slowapi, 5/min register, 10/min login
- ~~Missing authorization tests (member attempting delete should return 403)~~ — Fixed: 11 tests in test_authorization.py
- Frontend unit test coverage is thin (~7 test files for 40+ components)
- ~~`CLAUDE.md` says v0.5, should say v0.7~~ — Fixed

---

## Fix Summary

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| 1 | Critical | No auth on song create/update | Fixed |
| 2 | Critical | No auth on setlist create/update | Fixed |
| 3 | Critical | Exports bypass API base URL | Fixed |
| 4 | Critical | Backend healthcheck uses curl | Fixed |
| 5 | High | Calendar UTC date off-by-one | Fixed |
| 6 | High | PatternEditor no error handling | Fixed |
| 7 | High | E2E test suite broken | Fixed |
| 8 | High | HTML title says "frontend" | Fixed |
| 9 | Medium | CONTRIBUTING.md wrong port | Fixed |
| 10 | Medium | README.md stale "Coming Soon" | Fixed |
| 11 | Medium | .env.example blank VITE_API_URL | Fixed |
| 12 | Medium | Deprecated compose version key | Fixed |
| 13 | Medium | SongCard keyboard accessibility | Fixed |
| 14 | Medium | Containers run as root | Fixed |
