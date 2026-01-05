# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Javya is an open-source worship planning platform for church teams. It helps manage songs, build setlists, and export presentations. The name comes from Guaraní "javy'a" meaning "let us rejoice together."

## Current Status: v0.5 Complete

### Features
- **Authentication**: JWT-based login with bcrypt password hashing
- **Roles**: Admin > Leader > Member permission hierarchy
- **Availability**: Calendar-based availability tracking per user
- **Patterns**: Recurring availability (weekly/biweekly/monthly)
- **Scheduling**: Team scheduling with service role assignments
- **Assignments**: Assign team members to setlists with confirmation workflow
- **Songs**: Full CRUD, search/filter, detail view with lyrics/ChordPro
- **Setlists**: Create setlists with drag-and-drop song ordering
- **Export**: Export setlists to FreeShow (.project) and Quelea (.qsch)
- **Navigation**: Collapsible sidebar menu
- **i18n**: English and Spanish with language switcher
- **Backend**: FastAPI + async SQLAlchemy + PostgreSQL
- **Frontend**: React 19 + Vite + TypeScript + dnd-kit
- **Deployment**: Docker Compose

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19 + Vite + TypeScript + react-i18next |
| Backend | FastAPI + async SQLAlchemy + Pydantic |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Deployment | Docker Compose |

## Development Commands

### Start all services
```bash
docker compose up -d
```
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Backend commands
```bash
# Run all tests
docker compose exec backend pytest

# Run specific test file
docker compose exec backend pytest tests/test_songs.py -v

# Run database migrations
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# View logs
docker compose logs -f backend
```

### Frontend commands
```bash
# Install dependencies
docker compose exec frontend npm install

# Run dev server (already runs via docker compose)
docker compose exec frontend npm run dev
```

## API Endpoints

### Auth (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create account (first user = admin) |
| POST | `/login` | Get JWT token |
| GET | `/me` | Get current user |

### Users (`/api/v1/users`) — Admin/Leader only
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all users |
| PUT | `/{id}/role` | Change user role (admin only) |
| DELETE | `/{id}` | Deactivate user (admin only) |

### Songs (`/api/v1/songs`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List songs (supports `?search=`, `?key=`, `?mood=`, `?theme=`) |
| POST | `/` | Create song |
| GET | `/{id}` | Get song by ID |
| PUT | `/{id}` | Update song |
| DELETE | `/{id}` | Delete song (admin/leader only) |

### Setlists (`/api/v1/setlists`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List setlists (supports `?search=`, `?event_type=`) |
| POST | `/` | Create setlist with songs |
| GET | `/{id}` | Get setlist with songs |
| PUT | `/{id}` | Update setlist and songs |
| DELETE | `/{id}` | Delete setlist (admin/leader only) |
| GET | `/{id}/export/freeshow` | Export to FreeShow (.project) |
| GET | `/{id}/export/quelea` | Export to Quelea (.qsch) |

### Availability (`/api/v1/availability`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Set date availability |
| POST | `/bulk` | Set multiple dates at once |
| GET | `/me` | Get own availability (`?start_date=`, `?end_date=`) |
| GET | `/team` | Get team availability (admin/leader only) |
| DELETE | `/{id}` | Delete availability entry |
| POST | `/patterns` | Create recurring pattern |
| GET | `/patterns` | Get own patterns |
| PUT | `/patterns/{id}` | Update pattern |
| DELETE | `/patterns/{id}` | Delete pattern |

### Scheduling (`/api/v1/scheduling`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calendar` | Get setlists with assignments for date range |
| GET | `/my-assignments` | Get current user's assignments |
| GET | `/team-availability` | Check team availability for a date (admin/leader) |

### Setlist Assignments (`/api/v1/setlists/{id}/assignments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List assignments for setlist |
| POST | `/` | Create assignment (admin/leader only) |
| PUT | `/{assignment_id}` | Update assignment (admin/leader only) |
| DELETE | `/{assignment_id}` | Delete assignment (admin/leader only) |
| PATCH | `/{assignment_id}/confirm` | Confirm/unconfirm own assignment |

## Architecture

### Backend Structure (`backend/`)
```
app/
├── main.py          # FastAPI entry, CORS, routers
├── config.py        # Pydantic settings (includes JWT config)
├── database.py      # Async SQLAlchemy engine
├── models/          # SQLAlchemy ORM models (User, Song, Setlist, Availability, SetlistAssignment)
├── schemas/         # Pydantic request/response
├── routers/         # API route handlers (auth, users, songs, setlists, availability, scheduling)
├── services/        # Business logic (export generators)
├── auth/            # Security (password hashing, JWT, dependencies)
├── enums/           # UserRole, MusicalKey, Mood, Theme, EventType, AvailabilityStatus, ServiceRole
alembic/             # Database migrations
tests/               # Pytest test suite (116 tests)
```

### Frontend Structure (`frontend/`)
```
src/
├── api/             # API client and endpoints
│   ├── client.ts    # Fetch wrapper with JWT auth + timeout
│   ├── auth.ts      # Auth API (login, register)
│   ├── songs.ts     # Songs API methods
│   ├── setlists.ts  # Setlists API methods (CRUD + export)
│   ├── availability.ts # Availability API methods
│   └── scheduling.ts # Scheduling API methods
├── components/      # Reusable UI components
│   ├── Layout       # App layout with sidebar
│   ├── Sidebar      # Navigation sidebar
│   ├── ProtectedRoute # Auth route guard
│   ├── ErrorBoundary # Error boundary for graceful failures
│   ├── AvailabilityCalendar # Month calendar grid
│   ├── PatternEditor # Recurring pattern form
│   ├── ScheduleCalendar, ScheduleList # Scheduling views
│   ├── SetlistAssignmentEditor # Team assignment modal
│   ├── TeamRoster   # Team availability display
│   ├── SongCard, SongDetail, SongForm
│   ├── SetlistCard, SetlistForm, SetlistEditor
│   └── LanguageSwitcher
├── contexts/
│   └── AuthContext  # Auth state provider
├── pages/
│   ├── LoginPage    # Login/register form
│   ├── SongList     # Songs page
│   ├── SetlistList  # Setlists page
│   ├── AvailabilityPage # Availability calendar
│   └── SchedulingPage # Team scheduling calendar/list
├── hooks/           # Custom hooks (useSongs, useAvailability, useScheduling, etc.)
├── i18n/            # Translations (en, es)
└── types/           # TypeScript types (includes scheduling.ts)
```

### Key Patterns
- **Async everywhere**: All database operations use async/await
- **Dependency injection**: Database sessions via `Depends(get_db)`
- **UUID primary keys**: All models use UUID
- **API versioning**: Routes prefixed with `/api/v1/`

## Code Conventions

### Commits
Use conventional commits:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` tests
- `refactor:` code refactoring

### Python
- Type hints required
- Async functions for all DB operations
- Pydantic models for validation

### TypeScript
- Strict mode enabled
- Functional components with hooks
- Types in separate files

## Environment Variables

Set in `.env` or docker-compose:
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection (asyncpg driver) |
| `TEST_DATABASE_URL` | Test database connection |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `DEBUG` | Enable SQLAlchemy query logging |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens |
| `JWT_ALGORITHM` | JWT algorithm (default: HS256) |
| `JWT_EXPIRE_MINUTES` | Token expiration (default: 10080 = 7 days) |
