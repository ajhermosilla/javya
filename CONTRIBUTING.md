# Contributing to Javya

First off, thank you for considering contributing to Javya! 🎵

This project serves church worship teams, so every improvement helps communities come together in worship.

## How Can I Contribute?

### 🐛 Reporting Bugs

Found a bug? Please open an issue with:

1. **Clear title** describing the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs. what actually happened
4. **Screenshots** if applicable
5. **Environment info** (browser, OS, Docker version)

### 💡 Suggesting Features

Have an idea? Open an issue with the "enhancement" label:

1. **Describe the problem** you're trying to solve
2. **Describe your proposed solution**
3. **Consider alternatives** you've thought about
4. **Context** — how would this help your worship team?

### 🔧 Pull Requests

Ready to code? Here's the process:

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with clear, focused commits
4. **Test your changes** locally with Docker Compose
5. **Push** to your fork
6. **Open a Pull Request** against `main`

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/javya.git
cd javya

# Copy environment variables
cp .env.example .env

# Start development environment
docker compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Format with `black`
- Sort imports with `isort`

```bash
# Format code
black backend/
isort backend/
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Use the `t()` function for all user-facing text (i18n)
- Keep components small and focused

## Commit Messages

Write clear commit messages:

```
feat: add song search by theme
fix: correct key transposition calculation
docs: update README with Docker instructions
refactor: simplify setlist sorting logic
```

Prefixes: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Project Priorities

When contributing, keep these principles in mind:

1. **Reliability** — The app must work every Sunday morning
2. **Simplicity** — Non-technical worship leaders should find it intuitive
3. **Accessibility** — Multi-language support, mobile-friendly design
4. **Performance** — Should work well even on older devices

## Questions?

Open an issue with the "question" label, or start a discussion.

---

*Javy'a — Let us rejoice together* 🇵🇾
