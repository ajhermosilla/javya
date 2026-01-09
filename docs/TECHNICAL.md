# Javya Technical Documentation

Comprehensive technical reference for developers working on or integrating with Javya.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Database Schema](#database-schema)
5. [API Reference](#api-reference)
6. [Authentication & Security](#authentication--security)
7. [Development Guide](#development-guide)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Configuration Reference](#configuration-reference)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

Javya follows a modern three-tier architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                   React 19 + TypeScript + Vite                  │
│                      (Port 5173 / 80)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST + JWT
┌─────────────────────────▼───────────────────────────────────────┐
│                         Backend                                  │
│              FastAPI + async SQLAlchemy + Pydantic              │
│                        (Port 8000)                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ asyncpg
┌─────────────────────────▼───────────────────────────────────────┐
│                        Database                                  │
│                     PostgreSQL 16                                │
│                        (Port 5432)                               │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

- **Async-first**: All database operations are asynchronous
- **Type-safe**: Full type hints in Python, strict TypeScript
- **API-driven**: Clear separation between frontend and backend
- **UUID identifiers**: All entities use UUIDs for security and distribution
- **Soft deletes**: Users are deactivated, not deleted (preserves history)

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI 0.109+ | Async web framework with automatic OpenAPI docs |
| ORM | SQLAlchemy 2.0 (async) | Database abstraction with async support |
| Validation | Pydantic 2.0 | Request/response validation and serialization |
| Auth | python-jose + passlib | JWT tokens and bcrypt password hashing |
| PDF | WeasyPrint | PDF generation for chord charts and summaries |
| Migrations | Alembic | Database schema migrations |
| Testing | pytest + pytest-asyncio | Async test framework |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 19 | UI framework with hooks |
| Build | Vite 6 | Fast development and production builds |
| Language | TypeScript 5 | Type-safe JavaScript |
| Routing | React Router 7 | Client-side routing |
| Drag & Drop | dnd-kit | Accessible drag and drop for setlist ordering |
| i18n | react-i18next | Internationalization (EN, ES) |
| Testing | Vitest + Testing Library | Unit and component testing |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Database | PostgreSQL 16 | Primary data store |
| Containers | Docker + Compose | Development and production deployment |
| Proxy (prod) | nginx | Static file serving and reverse proxy |
| CI/CD | GitHub Actions | Automated testing and builds |

---

## Project Structure

```
javya/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Pydantic settings from environment
│   │   ├── database.py          # Async SQLAlchemy engine and session
│   │   ├── middleware.py        # Security headers middleware
│   │   ├── utils.py             # Shared utility functions
│   │   ├── auth/
│   │   │   ├── security.py      # Password hashing, JWT creation
│   │   │   └── dependencies.py  # FastAPI dependencies (get_current_user, require_role)
│   │   ├── models/
│   │   │   ├── user.py          # User model
│   │   │   ├── song.py          # Song model
│   │   │   ├── setlist.py       # Setlist model
│   │   │   ├── setlist_song.py  # Setlist-Song join table
│   │   │   ├── setlist_assignment.py  # Team assignments
│   │   │   ├── availability.py  # Date availability
│   │   │   └── availability_pattern.py  # Recurring patterns
│   │   ├── schemas/
│   │   │   ├── user.py          # User request/response schemas
│   │   │   ├── song.py          # Song schemas with validation
│   │   │   ├── setlist.py       # Setlist schemas
│   │   │   ├── setlist_assignment.py  # Assignment schemas
│   │   │   ├── availability.py  # Availability schemas
│   │   │   ├── duplicate.py     # Duplicate detection schemas
│   │   │   └── import_song.py   # Song import schemas
│   │   ├── routers/
│   │   │   ├── auth.py          # /api/v1/auth/*
│   │   │   ├── users.py         # /api/v1/users/*
│   │   │   ├── songs.py         # /api/v1/songs/*
│   │   │   ├── setlists.py      # /api/v1/setlists/*
│   │   │   ├── availability.py  # /api/v1/availability/*
│   │   │   ├── scheduling.py    # /api/v1/scheduling/*
│   │   │   └── import_songs.py  # /api/v1/songs/import/*
│   │   ├── services/
│   │   │   ├── export_freeshow.py   # FreeShow .project export
│   │   │   ├── export_quelea.py     # Quelea .qsch export
│   │   │   ├── export_pdf.py        # PDF chord charts and summaries
│   │   │   ├── duplicate_detector.py # Song duplicate detection
│   │   │   └── import_song/         # Multi-format song import
│   │   │       ├── detector.py      # Format auto-detection
│   │   │       ├── chordpro_parser.py
│   │   │       ├── openlyrics_parser.py
│   │   │       ├── opensong_parser.py
│   │   │       └── plaintext_parser.py
│   │   ├── enums/
│   │   │   ├── user_role.py     # admin, leader, member
│   │   │   ├── musical_key.py   # C, C#, Db, D, etc.
│   │   │   ├── mood.py          # Joyful, Reflective, etc.
│   │   │   ├── theme.py         # Worship, Communion, etc.
│   │   │   ├── event_type.py    # sunday_service, special, etc.
│   │   │   ├── service_role.py  # worship_leader, vocalist, etc.
│   │   │   └── availability_status.py  # available, unavailable, tentative
│   │   └── templates/
│   │       └── pdf/             # HTML templates for PDF generation
│   ├── alembic/
│   │   └── versions/            # Database migrations
│   ├── tests/
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── test_auth.py
│   │   ├── test_songs.py
│   │   ├── test_setlists.py
│   │   ├── test_availability.py
│   │   ├── test_import_*.py
│   │   └── fixtures/            # Test data files
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── App.tsx              # Root component with routing
│   │   ├── api/
│   │   │   ├── client.ts        # Fetch wrapper with JWT and timeout
│   │   │   ├── auth.ts          # Login, register, getCurrentUser
│   │   │   ├── songs.ts         # Song CRUD + duplicate check
│   │   │   ├── setlists.ts      # Setlist CRUD + export
│   │   │   ├── availability.ts  # Availability and patterns
│   │   │   ├── scheduling.ts    # Calendar and assignments
│   │   │   └── import.ts        # Song import API
│   │   ├── components/
│   │   │   ├── Layout.tsx       # App shell with sidebar
│   │   │   ├── Sidebar.tsx      # Navigation menu
│   │   │   ├── ProtectedRoute.tsx  # Auth guard
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── SearchBar.tsx    # Debounced search input
│   │   │   ├── FilterBar.tsx    # Key/mood/theme filters
│   │   │   ├── SongCard.tsx, SongDetail.tsx, SongForm.tsx
│   │   │   ├── SetlistCard.tsx, SetlistForm.tsx, SetlistEditor.tsx
│   │   │   ├── AvailabilityCalendar.tsx, PatternEditor.tsx
│   │   │   ├── ScheduleCalendar.tsx, ScheduleList.tsx
│   │   │   ├── SetlistAssignmentEditor.tsx
│   │   │   ├── ImportModal.tsx, ImportPreview.tsx
│   │   │   ├── DuplicateWarning.tsx
│   │   │   └── LanguageSwitcher.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx    # Login/register forms
│   │   │   ├── SongList.tsx     # Songs management
│   │   │   ├── SetlistList.tsx  # Setlists management
│   │   │   ├── AvailabilityPage.tsx  # Personal availability
│   │   │   └── SchedulingPage.tsx    # Team scheduling
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx  # Auth state provider
│   │   ├── hooks/
│   │   │   ├── useSongs.ts
│   │   │   ├── useSetlists.ts
│   │   │   ├── useAvailability.ts
│   │   │   ├── useScheduling.ts
│   │   │   └── useDebounce.ts
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   ├── song.ts
│   │   │   ├── setlist.ts
│   │   │   ├── availability.ts
│   │   │   ├── scheduling.ts
│   │   │   └── import.ts
│   │   ├── i18n/
│   │   │   ├── index.ts         # i18next configuration
│   │   │   └── locales/
│   │   │       ├── en.json      # English translations
│   │   │       └── es.json      # Spanish translations
│   │   ├── utils/
│   │   │   └── transpose.ts     # Chord transposition utilities
│   │   └── test/
│   │       └── utils.tsx        # Test utilities and providers
│   ├── Dockerfile               # Development Dockerfile
│   ├── Dockerfile.prod          # Production multi-stage build
│   ├── nginx.conf               # Production nginx config
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── docs/
│   ├── TECHNICAL.md             # This file
│   ├── QUICKSTART.md            # User quickstart guide
│   ├── codebase-review-*.md     # Code review reports
│   └── session-*.md             # Development session summaries
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
│
├── docker-compose.yml           # Development configuration
├── docker-compose.prod.yml      # Production configuration
├── README.md
├── ROADMAP.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │    Song     │       │   Setlist   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ email       │       │ name        │       │ name        │
│ name        │       │ artist      │       │ description │
│ password    │       │ lyrics      │       │ service_date│
│ role        │       │ chordpro    │       │ event_type  │
│ is_active   │       │ original_key│       │ created_at  │
│ created_at  │       │ preferred_key       │ updated_at  │
│ updated_at  │       │ tempo_bpm   │       └──────┬──────┘
└──────┬──────┘       │ mood        │              │
       │              │ themes[]    │              │
       │              │ url         │              │
       │              │ min_band[]  │              │
       │              │ notes       │              │
       │              │ created_at  │              │
       │              │ updated_at  │              │
       │              └──────┬──────┘              │
       │                     │                     │
       │              ┌──────▼──────┐              │
       │              │ SetlistSong │◄─────────────┘
       │              ├─────────────┤
       │              │ id (PK)     │
       │              │ setlist_id  │
       │              │ song_id     │
       │              │ position    │
       │              │ notes       │
       │              └─────────────┘
       │
       ├──────────────────────────────────────────┐
       │                                          │
       ▼                                          ▼
┌─────────────────┐                    ┌─────────────────────┐
│  Availability   │                    │ SetlistAssignment   │
├─────────────────┤                    ├─────────────────────┤
│ id (PK)         │                    │ id (PK)             │
│ user_id (FK)    │                    │ setlist_id (FK)     │
│ date            │                    │ user_id (FK)        │
│ status          │                    │ service_role        │
│ note            │                    │ notes               │
│ created_at      │                    │ confirmed           │
│ updated_at      │                    │ created_at          │
└─────────────────┘                    │ updated_at          │
                                       └─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ AvailabilityPattern │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ day_of_week (0-6)   │
│ frequency           │
│ status              │
│ start_date          │
│ end_date            │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

### Key Constraints

- `users.email` — Unique index
- `availability(user_id, date)` — Unique constraint (one entry per user per date)
- `setlist_assignments(setlist_id, user_id, service_role)` — Unique constraint
- `setlist_songs.setlist_id` — Indexed for performance
- All foreign keys have `ON DELETE CASCADE`

### Enums

**UserRole**: `admin`, `leader`, `member`

**MusicalKey**: `C`, `C#`, `Db`, `D`, `D#`, `Eb`, `E`, `F`, `F#`, `Gb`, `G`, `G#`, `Ab`, `A`, `A#`, `Bb`, `B`

**Mood**: `Joyful`, `Reflective`, `Triumphant`, `Intimate`, `Peaceful`, `Energetic`, `Hopeful`, `Solemn`, `Celebratory`

**Theme**: `Worship`, `Communion`, `Offering`, `Opening`, `Closing`, `Prayer`, `Declaration`, `Thanksgiving`, `Faith`, `Grace`, `Salvation`, `Baptism`, `Christmas`, `Holy Week`

**EventType**: `sunday_service`, `wednesday_service`, `special`, `rehearsal`, `other`

**AvailabilityStatus**: `available`, `unavailable`, `tentative`

**ServiceRole**: `worship_leader`, `vocalist`, `acoustic_guitar`, `electric_guitar`, `bass`, `drums`, `keys`, `sound`, `projection`, `other`

---

## API Reference

Base URL: `/api/v1`

### Authentication

All endpoints except `/auth/register` and `/auth/login` require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

#### POST /auth/register

Create a new user account. First user becomes admin.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-01-09T12:00:00Z",
  "updated_at": "2026-01-09T12:00:00Z"
}
```

#### POST /auth/login

Get a JWT token. Uses OAuth2 password flow.

**Request:** `application/x-www-form-urlencoded`
```
username=user@example.com&password=securepassword
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### GET /auth/me

Get current authenticated user.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-01-09T12:00:00Z",
  "updated_at": "2026-01-09T12:00:00Z"
}
```

### Songs

#### GET /songs

List songs with optional filters.

**Query Parameters:**
- `search` — Search in name and artist
- `key` — Filter by musical key
- `mood` — Filter by mood
- `theme` — Filter by theme
- `limit` — Max results (default: 50, max: 100)
- `offset` — Pagination offset

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Amazing Grace",
    "artist": "John Newton",
    "original_key": "G",
    "preferred_key": "A",
    "tempo_bpm": 72,
    "mood": "Peaceful",
    "themes": ["Worship", "Grace"],
    "lyrics": "Amazing grace, how sweet...",
    "chordpro_chart": "[G]Amazing [C]grace...",
    "url": "https://youtube.com/...",
    "min_band": ["acoustic guitar", "vocals"],
    "notes": "Start softly",
    "created_at": "2026-01-09T12:00:00Z",
    "updated_at": "2026-01-09T12:00:00Z"
  }
]
```

#### POST /songs

Create a new song.

**Request:**
```json
{
  "name": "Amazing Grace",
  "artist": "John Newton",
  "original_key": "G",
  "preferred_key": "A",
  "tempo_bpm": 72,
  "mood": "Peaceful",
  "themes": ["Worship", "Grace"],
  "lyrics": "Amazing grace, how sweet...",
  "chordpro_chart": "[G]Amazing [C]grace...",
  "url": "https://youtube.com/...",
  "min_band": ["acoustic guitar", "vocals"],
  "notes": "Start softly"
}
```

**Response:** `201 Created`

#### GET /songs/{id}

Get a song by ID.

#### PUT /songs/{id}

Update a song.

#### DELETE /songs/{id}

Delete a song. Requires `admin` or `leader` role.

#### POST /songs/check-duplicates

Check for duplicate songs before import.

**Request:**
```json
{
  "songs": [
    {"name": "Amazing Grace", "artist": "John Newton"}
  ]
}
```

**Response:**
```json
{
  "duplicates": [
    {
      "input_index": 0,
      "input_name": "Amazing Grace",
      "existing_song": {
        "id": "uuid",
        "name": "Amazing Grace",
        "artist": "John Newton"
      },
      "match_type": "exact"
    }
  ]
}
```

### Song Import

#### POST /songs/import/preview

Upload files for parsing preview.

**Request:** `multipart/form-data`
- `files` — Up to 20 files, 1MB each
- Supported formats: ChordPro (.cho, .crd, .chopro), OpenLyrics (.xml), OpenSong (.xml), Plain text (.txt)

**Response:**
```json
{
  "results": [
    {
      "filename": "amazing_grace.cho",
      "success": true,
      "format": "chordpro",
      "song": {
        "name": "Amazing Grace",
        "artist": "John Newton",
        "original_key": "G",
        "chordpro_chart": "[G]Amazing [C]grace..."
      }
    }
  ]
}
```

#### POST /songs/import/confirm

Save selected songs from preview.

**Request:**
```json
{
  "songs": [
    {
      "name": "Amazing Grace",
      "artist": "John Newton",
      "original_key": "G",
      "chordpro_chart": "[G]Amazing [C]grace..."
    }
  ]
}
```

### Setlists

#### GET /setlists

List setlists with optional filters.

**Query Parameters:**
- `search` — Search in name
- `event_type` — Filter by event type
- `limit`, `offset` — Pagination

#### POST /setlists

Create a setlist with songs.

**Request:**
```json
{
  "name": "Sunday Morning",
  "description": "Regular service",
  "service_date": "2026-01-12",
  "event_type": "sunday_service",
  "songs": [
    {"song_id": "uuid", "position": 0, "notes": "Key of A"},
    {"song_id": "uuid", "position": 1}
  ]
}
```

#### GET /setlists/{id}

Get setlist with all songs.

#### PUT /setlists/{id}

Update setlist (replaces songs array).

#### DELETE /setlists/{id}

Delete setlist. Requires `admin` or `leader` role.

#### GET /setlists/{id}/export/freeshow

Export to FreeShow format (.project JSON).

#### GET /setlists/{id}/export/quelea

Export to Quelea format (.qsch XML).

#### GET /setlists/{id}/export/pdf

Export to PDF.

**Query Parameters:**
- `format` — `summary` (song list) or `chords` (chord charts)

### Setlist Assignments

#### GET /setlists/{id}/assignments

List assignments for a setlist.

#### POST /setlists/{id}/assignments

Create an assignment. Requires `admin` or `leader` role.

**Request:**
```json
{
  "user_id": "uuid",
  "service_role": "worship_leader",
  "notes": "Lead first 3 songs"
}
```

#### PUT /setlists/{id}/assignments/{assignment_id}

Update assignment.

#### DELETE /setlists/{id}/assignments/{assignment_id}

Delete assignment.

#### PATCH /setlists/{id}/assignments/{assignment_id}/confirm

Confirm or unconfirm own assignment.

**Request:**
```json
{
  "confirmed": true
}
```

### Availability

#### POST /availability

Set availability for a date.

**Request:**
```json
{
  "date": "2026-01-12",
  "status": "available",
  "note": "Available all day"
}
```

#### POST /availability/bulk

Set availability for multiple dates.

#### GET /availability/me

Get own availability for date range.

**Query Parameters:**
- `start_date` — Start of range
- `end_date` — End of range

#### GET /availability/team

Get team availability (admin/leader only).

#### POST /availability/patterns

Create recurring availability pattern.

**Request:**
```json
{
  "day_of_week": 0,
  "frequency": "weekly",
  "status": "available",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31"
}
```

### Scheduling

#### GET /scheduling/calendar

Get setlists with assignments for calendar view.

**Query Parameters:**
- `start_date` — Start of range (required)
- `end_date` — End of range (required)

#### GET /scheduling/my-assignments

Get current user's assignments.

**Query Parameters:**
- `upcoming_only` — Only show future assignments (default: true)

#### GET /scheduling/availability

Get team member availability for a date (admin/leader only).

---

## Authentication & Security

### JWT Implementation

- Algorithm: HS256 (configurable)
- Expiration: 7 days (configurable)
- Token includes: `sub` (user email), `exp` (expiration timestamp)

### Password Security

- Hashing: bcrypt with automatic salt
- Minimum password length enforced at frontend

### Role-Based Access Control

| Action | Admin | Leader | Member |
|--------|-------|--------|--------|
| View songs/setlists | ✓ | ✓ | ✓ |
| Create songs/setlists | ✓ | ✓ | ✓ |
| Delete songs/setlists | ✓ | ✓ | ✗ |
| Manage users | ✓ | ✗ | ✗ |
| Change roles | ✓ | ✗ | ✗ |
| Create assignments | ✓ | ✓ | ✗ |
| View team availability | ✓ | ✓ | ✗ |
| Confirm own assignment | ✓ | ✓ | ✓ |

### Security Headers

Production deployment includes:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; ...
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### CORS Configuration

Development allows `localhost:3000` and `localhost:5173`.
Production requires explicit `CORS_ORIGINS` configuration.

---

## Development Guide

### Prerequisites

- Docker & Docker Compose
- Git
- (Optional) Node.js 20+ for frontend development outside Docker
- (Optional) Python 3.12+ for backend development outside Docker

### Getting Started

```bash
# Clone repository
git clone https://github.com/ajhermosilla/javya.git
cd javya

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Access services
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Development Workflow

```bash
# Backend: Run tests
docker compose exec backend pytest

# Backend: Run specific test file
docker compose exec backend pytest tests/test_songs.py -v

# Backend: Create migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Backend: Apply migrations
docker compose exec backend alembic upgrade head

# Frontend: Run tests
docker compose exec frontend npm test -- --run

# Frontend: Type check
docker compose exec frontend npm run build
```

### Code Style

**Python:**
- Type hints required for all functions
- Async functions for all database operations
- Pydantic models for all API validation
- Follow FastAPI conventions

**TypeScript:**
- Strict mode enabled
- Functional components with hooks
- Types in separate files under `types/`
- Use `ApiError` for all API error handling

### Commit Convention

Use conventional commits:
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `test:` — Tests
- `refactor:` — Code refactoring
- `chore:` — Maintenance

---

## Testing

### Backend Tests

```bash
# Run all tests
docker compose exec backend pytest

# Run with coverage
docker compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker compose exec backend pytest tests/test_songs.py -v

# Run tests matching pattern
docker compose exec backend pytest -k "test_create"
```

**Test Categories:**
- `test_auth.py` — Authentication and authorization
- `test_songs.py` — Song CRUD operations
- `test_setlists.py` — Setlist management
- `test_availability.py` — Availability and patterns
- `test_setlist_assignments.py` — Team assignments
- `test_import_*.py` — Song import parsing
- `test_export_pdf.py` — PDF generation
- `test_duplicate_detection.py` — Duplicate song detection

### Frontend Tests

```bash
# Run all tests
docker compose exec frontend npm test -- --run

# Run with coverage
docker compose exec frontend npm test -- --coverage

# Run in watch mode
docker compose exec frontend npm test
```

### E2E Tests

The CI pipeline includes E2E tests that verify the full stack.

---

## Deployment

### Development (Docker Compose)

```bash
docker compose up -d
```

Uses development configurations:
- Hot reload enabled
- Debug mode on
- Source volumes mounted
- Default credentials (change in production!)

### Production (Docker Compose)

```bash
# Generate secrets
export POSTGRES_PASSWORD=$(openssl rand -hex 32)
export SECRET_KEY=$(openssl rand -hex 32)
export CORS_ORIGINS=https://your-domain.com

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

**Production differences:**
- No source volume mounts
- 4 uvicorn workers
- nginx for frontend
- Required secrets via environment
- Security headers enabled
- Debug mode disabled

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `SECRET_KEY` | Yes | — | JWT signing key (generate with `openssl rand -hex 32`) |
| `POSTGRES_PASSWORD` | Yes | — | Database password |
| `CORS_ORIGINS` | Yes | — | Comma-separated allowed origins |
| `DEBUG` | No | `false` | Enable debug logging |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_EXPIRE_MINUTES` | No | `10080` | Token expiration (7 days) |

---

## Configuration Reference

### Backend Configuration (`backend/app/config.py`)

```python
class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "http://localhost:5173"
```

### Frontend Configuration

Environment variables (set at build time for production):
- `VITE_API_URL` — Backend API URL (empty for same-origin)

---

## Troubleshooting

### Database Connection Errors

```bash
# Check if database is running
docker compose ps

# View database logs
docker compose logs db

# Reset database
docker compose down -v
docker compose up -d
```

### Migration Errors

```bash
# Check current migration status
docker compose exec backend alembic current

# Reset to specific revision
docker compose exec backend alembic downgrade <revision>

# Generate new migration
docker compose exec backend alembic revision --autogenerate -m "description"
```

### Frontend Build Errors

```bash
# Clear node_modules
docker compose exec frontend rm -rf node_modules
docker compose exec frontend npm install

# Rebuild container
docker compose build frontend
```

### Authentication Issues

- Check JWT token expiration
- Verify `SECRET_KEY` matches between instances
- Clear browser localStorage and re-login

### CORS Errors

- Verify `CORS_ORIGINS` includes your frontend URL
- Check for trailing slashes (should not have them)
- Ensure protocol matches (http vs https)

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [ChordPro Format](https://www.chordpro.org/)
