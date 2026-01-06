# Changelog

All notable changes to Javya will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-01-05

### Added
- **Team scheduling** — Calendar view showing setlists and service dates
- **Service role assignments** — Assign team members to roles (worship leader, vocalist, guitarist, bassist, drummer, keys, sound, projection)
- **Assignment confirmation** — Track confirmed vs pending assignments
- **PDF export for musicians** — Two export modes:
  - Summary: Quick reference with song titles, keys, tempo, artist
  - Chord charts: Full ChordPro lyrics with inline chords for rehearsals
- ChordPro parser that renders styled chord annotations
- Service roles enum and assignments API endpoints
- Scheduling page with calendar and list views
- Assignment editor modal with role selection

### Fixed
- Race condition in bulk availability updates (using PostgreSQL upsert)
- Pattern date validation (end date must be after start date)
- Enum value conversion in pattern updates
- Authentication requirement on export endpoints
- Modal header overlap with close button
- Loading states and error handling in frontend

## [0.4.0] - 2025-01-04

### Added
- **JWT authentication** — Secure login with access tokens
- **User roles** — Admin, Leader, and Member permission hierarchy
- **User management** — Admins can change roles and deactivate users
- **Availability calendar** — Track team member availability by date
- **Recurring patterns** — Set weekly, biweekly, or monthly availability
- First registered user automatically becomes Admin
- Password hashing with bcrypt
- Protected routes in frontend

### Changed
- All API endpoints now require authentication
- Song and setlist deletion restricted to Admin and Leader roles

## [0.3.0] - 2025-01-03

### Added
- **Setlist builder** — Create setlists with drag-and-drop song ordering
- **Export to FreeShow** — Generate .project files for FreeShow presentation software
- **Export to Quelea** — Generate .qsch files for Quelea projection software
- Setlist CRUD API endpoints
- SetlistEditor component with DnD Kit
- SongPicker for adding songs to setlists
- Event type classification (Sunday, Wednesday, Youth, Special, Retreat, Other)

## [0.2.0] - 2025-01-02

### Added
- **Song database** — Full CRUD operations for songs
- **ChordPro support** — Store chord charts in ChordPro format
- **Search and filter** — Find songs by name, key, mood, or theme
- **Multi-language support** — English and Spanish translations
- Song detail view with lyrics and metadata
- Musical key, mood, and theme enums
- Collapsible sidebar navigation
- Language switcher component

## [0.1.0] - 2025-01-01

### Added
- Initial project setup with Docker Compose
- FastAPI backend with async SQLAlchemy
- React 19 frontend with Vite and TypeScript
- PostgreSQL 16 database
- Basic project structure and configuration
- API documentation with Swagger UI

---

[0.5.0]: https://github.com/ajhermosilla/javya/compare/v0.4...v0.5
[0.4.0]: https://github.com/ajhermosilla/javya/compare/v0.3...v0.4
[0.3.0]: https://github.com/ajhermosilla/javya/compare/v0.2...v0.3
[0.2.0]: https://github.com/ajhermosilla/javya/compare/v0.1...v0.2
[0.1.0]: https://github.com/ajhermosilla/javya/releases/tag/v0.1
