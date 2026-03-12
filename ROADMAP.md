# Roadmap

This document outlines planned features for Javya. We welcome community input—open an issue or discussion to share your ideas!

---

## Completed

### v0.7 — Advanced Song Import ✅
- [x] Clipboard paste — Paste lyrics directly without needing a file
- [x] URL import — Fetch song content from a URL
- [x] Edit before import — Modify parsed fields in preview before saving
- [x] ZIP archive support — Import entire song libraries at once
- [x] OnSong format — Support for popular iOS app format (.onsong)

### v0.6 — Song Tools ✅
- [x] Song transposition — Transpose ChordPro charts to any key with capo suggestions
- [x] Song import — Import from Ultimate Guitar, ChordPro, OpenLyrics, OpenSong, or plain text
- [x] Song duplicates detection — Warn when adding similar songs

### v0.5 — Team Scheduling ✅
- [x] Team scheduling calendar view
- [x] Service role assignments (worship leader, vocalist, guitarist, etc.)
- [x] Assignment confirmation workflow
- [x] PDF export for musicians (summary and chord charts)

### v0.4 — Core Platform ✅
- [x] JWT authentication with role-based access (Admin, Leader, Member)
- [x] Song database with lyrics, ChordPro charts, keys, mood, themes
- [x] Setlist builder with drag-and-drop ordering
- [x] Export to FreeShow (.project) and Quelea (.qsch)
- [x] Availability calendar with recurring patterns
- [x] Multi-language support (English, Spanish)

---

## Current Cycle: First Users (4 weeks, Mar 2026)

The goal of this cycle is to get Javya in front of a real worship team and iterate based on feedback. Everything below serves that goal.

### Week 1 — Make It Ready

Prep work so the team can start using it this Sunday.

- [ ] **Seed song library** — Import existing church songs (ChordPro, OpenLyrics, or plain text)
- [ ] **PWA support** — Add manifest.json, service worker, and app icons so team members can install it on their phones
- [ ] **Fix HTML title** — Currently shows "frontend" instead of "Javya"
- [ ] **Empty states** — Show helpful guidance on pages with no data (no songs yet, no setlists, empty calendar)
- [ ] **First-login experience** — Admin hint on first login (e.g., "Start by adding songs or inviting your team")

### Week 2 — Put It in Their Hands

Roll out to the worship team and collect real feedback.

- [ ] **Create team accounts** — Register team members or have them self-register
- [ ] **Build first real setlist** — Use Javya for this Sunday's service
- [ ] **Assign roles and availability** — Full scheduling workflow with real people
- [ ] **Collect feedback** — Track what's confusing, what's missing, what breaks
- [ ] **Quick fixes** — Address blocking issues as they come in

### Week 3 — Top Feedback + Notifications

Fix the biggest pain points and add the #1 missing feature for adoption.

- [ ] **Fix top UX issues** — Address 3-5 highest-priority items from team feedback
- [ ] **Assignment notifications** — Notify team members when they're assigned to a service (email or push)
- [ ] **Schedule reminders** — Automated reminders before services
- [ ] **Merge with existing songs** — Update existing songs instead of creating duplicates

### Week 4 — Stabilize + Plan

Second service cycle with improvements. Solidify what works.

- [ ] **Second Sunday** — Team uses Javya again with Week 3 improvements
- [ ] **Fix regressions** — Address anything broken by Week 3 changes
- [ ] **Dashboard MVP** — Simple landing page showing upcoming services and pending assignments
- [ ] **Retrospective** — Document what worked, what didn't, decide next priorities

---

## Planned Features

### v0.8 — Notifications & Communication
- [ ] **Availability requests** — Leaders can request availability for specific dates
- [ ] **In-app messaging** — Team chat per setlist/service

### v0.9 — Dashboard & Analytics
- [ ] **Song usage stats** — Track how often songs are used
- [ ] **Team participation** — View member contribution over time
- [ ] **Service history** — Archive of past setlists with notes

### v0.10 — Mobile & Offline
- [ ] **Offline mode** — Access setlists and songs without internet
- [ ] **Practice mode** — Audio/video playback with synced lyrics
- [ ] **Smarter parsing** — Auto-detect key from chord progressions

### v1.0 — Integrations
- [ ] **Calendar sync** — Export schedules to Google Calendar / iCal
- [ ] **Projection software** — Direct push to ProPresenter, EasyWorship, OpenLP
- [ ] **Cloud backup** — Automatic backups to Google Drive / Dropbox
- [ ] **API access** — Public API for custom integrations

---

## Future Ideas

These are features we're considering but haven't scheduled yet:

- **Multi-church support** — Manage multiple congregations from one account
- **Guest musicians** — Invite external team members for special services
- **Rehearsal scheduling** — Plan and track band rehearsals
- **Song arrangements** — Store multiple arrangements per song
- **Setlist templates** — Save and reuse common service structures
- **Dark mode** — Theme toggle for low-light environments
- **Português support** — Add Brazilian Portuguese translations
- **Guaraní support** — Add native Guaraní translations

---

## How to Contribute

We prioritize features that help worship teams serve their communities better. If you'd like to contribute:

1. **Discuss first** — Open an issue to discuss the feature before coding
2. **Keep it simple** — Non-technical worship leaders should find it intuitive
3. **Test thoroughly** — It must work reliably every Sunday

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

<p align="center">
  <i>Have a feature request? <a href="https://github.com/ajhermosilla/javya/issues/new">Open an issue</a>!</i>
</p>
