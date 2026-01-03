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

### v0.1 (Current)
- [x] Song database with lyrics, chords, keys, mood, and themes
- [x] ChordPro chart storage
- [x] Search and filter songs
- [x] Multi-language support (English, Spanish)

### Roadmap
- [ ] **v0.2** — Setlist builder with drag-and-drop
- [ ] **v0.3** — Export to Quelea/FreeShow presentation software
- [ ] **v0.4** — Team availability and scheduling

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| i18n | react-i18next |
| Deployment | Docker Compose |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Run locally

```bash
# Clone the repo
git clone https://github.com/ajhermosilla/javya.git
cd javya

# Start all services
docker compose up -d

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Project Structure

```
javya/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API routes
│   │   └── enums/            # Mood, Theme, Key enums
│   ├── alembic/              # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
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
