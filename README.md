# 🎵 Javya

**Open-source worship planning for church teams.**

Javya (from Guaraní *javy'a* — "let us rejoice together") is a web-based platform that helps worship teams manage songs, build setlists, and export presentations. Born in Asunción, Paraguay.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made in Paraguay](https://img.shields.io/badge/Made%20in-Paraguay%20🇵🇾-blue)]()

---

## The Problem

Most worship teams juggle disconnected tools:

- Google Sheets for scheduling
- PowerPoint for lyrics (inconsistent templates, missing verses)
- Songbook Pro for chords
- WhatsApp for coordination
- YouTube links scattered everywhere

Javya consolidates this into one reliable tool.

---

## Features

### Core Features
- **Song Management** — Lyrics, ChordPro chords, keys, tempo, mood, themes
- **Setlist Builder** — Drag-and-drop ordering with notes per song
- **Team Scheduling** — Calendar view with role assignments and confirmations
- **Availability Tracking** — Personal calendars with recurring patterns
- **Multi-format Export** — FreeShow, Quelea, PDF summaries and chord charts
- **Song Import** — Bulk import from ChordPro, OpenLyrics, OpenSong, plain text
- **Duplicate Detection** — Smart matching when importing songs
- **Role-based Access** — Admin, Leader, Member permission hierarchy
- **Multi-language** — English and Spanish with easy extensibility

### Coming Soon
See our full **[Roadmap](ROADMAP.md)** for planned features including:
- Song transposition tool
- CCLI integration
- Email notifications
- Dashboard and analytics
- Mobile app

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19 + Vite + TypeScript |
| Backend | FastAPI + async SQLAlchemy |
| Database | PostgreSQL 16 |
| Auth | JWT + bcrypt |
| i18n | react-i18next |
| Deployment | Docker Compose |

---

## Quick Start

```bash
# Clone and start
git clone https://github.com/ajhermosilla/javya.git
cd javya
docker compose up -d

# Open http://localhost:5173
# First user becomes Admin
```

**Requirements:** Docker & Docker Compose

See the **[Quickstart Guide](docs/QUICKSTART.md)** for detailed setup instructions.

---

## Documentation

| Document | Audience | Description |
|----------|----------|-------------|
| [Quickstart Guide](docs/QUICKSTART.md) | Users | Get started in 10 minutes |
| [Technical Docs](docs/TECHNICAL.md) | Developers | Architecture, API, deployment |
| [Roadmap](ROADMAP.md) | Everyone | Planned features |
| [Contributing](CONTRIBUTING.md) | Contributors | How to contribute |
| [Changelog](CHANGELOG.md) | Everyone | Version history |

---

## Project Structure

```
javya/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── models/           # SQLAlchemy models (User, Song, Setlist, Availability)
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API routes (auth, songs, setlists, availability)
│   │   ├── services/         # Export generators (FreeShow, Quelea, PDF)
│   │   ├── templates/        # HTML templates for PDF generation
│   │   ├── auth/             # JWT security & dependencies
│   │   └── enums/            # Role, Mood, Theme, Key, EventType enums
│   ├── alembic/              # Database migrations
│   └── tests/                # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # Auth context
│   │   ├── hooks/            # Custom hooks
│   │   ├── api/              # API client
│   │   └── i18n/             # Translations (en, es)
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Contributing

Contributions welcome! This project serves church communities, so we prioritize:

1. **Reliability** — It must work every Sunday
2. **Simplicity** — Non-technical worship leaders should find it intuitive
3. **Accessibility** — Multi-language, mobile-friendly

### How to contribute

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License — use it freely, even commercially. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built for the worship team at ICE Renuevo, Asunción, Paraguay
- Name inspired by Guaraní language and culture
- ChordPro format by [chordpro.org](https://www.chordpro.org/)

---

<p align="center">
  <i>Javy'a — Let us rejoice together 🇵🇾</i>
</p>
