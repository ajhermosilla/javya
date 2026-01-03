# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Javya is an open-source worship planning platform for church teams. It helps manage songs, build setlists, and export presentations. The name comes from Guaraní "javy'a" meaning "let us rejoice together."

## Current Status: v0.2 Complete

### Features
- **Songs**: Full CRUD, search/filter, detail view with lyrics/ChordPro
- **Setlists**: Create setlists with drag-and-drop song ordering
- **Navigation**: Collapsible sidebar menu
- **i18n**: English and Spanish with language switcher
- **Backend**: FastAPI + async SQLAlchemy + PostgreSQL
- **Frontend**: React + Vite + TypeScript + dnd-kit
- **Deployment**: Docker Compose

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite + TypeScript + react-i18next |
| Backend | FastAPI + async SQLAlchemy + Pydantic |
| Database | PostgreSQL 16 |
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

### Songs (`/api/v1/songs`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List songs (supports `?search=`, `?key=`, `?mood=`, `?theme=`) |
| POST | `/` | Create song |
| GET | `/{id}` | Get song by ID |
| PUT | `/{id}` | Update song |
| DELETE | `/{id}` | Delete song |

## Architecture

### Backend Structure (`backend/`)
```
app/
├── main.py          # FastAPI entry, CORS, routers
├── config.py        # Pydantic settings
├── database.py      # Async SQLAlchemy engine
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response
├── routers/         # API route handlers
├── enums/           # MusicalKey, Mood, Theme
alembic/             # Database migrations
tests/               # Pytest test suite
```

### Frontend Structure (`frontend/`)
```
src/
├── api/             # API client and endpoints
│   ├── client.ts    # Fetch wrapper with error handling
│   └── songs.ts     # Songs API methods
├── components/      # Reusable UI components
│   ├── SongCard     # Song card with metadata
│   ├── SongDetail   # Full song view with lyrics
│   ├── SongForm     # Create/edit form
│   ├── SearchBar    # Search input
│   ├── FilterBar    # Key/mood/theme filters
│   └── LanguageSwitcher
├── pages/
│   └── SongList     # Main page with list/detail/form views
├── hooks/
│   └── useSongs.ts  # Data fetching hook
├── i18n/            # Translations (en, es)
└── types/           # TypeScript types
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
