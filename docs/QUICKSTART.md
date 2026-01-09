# Javya Quickstart Guide

Get your worship team organized in 10 minutes.

---

## What is Javya?

Javya is a free, open-source tool that helps worship teams:

- **Manage songs** — Store lyrics, chords, keys, and reference links in one place
- **Build setlists** — Create service orders with drag-and-drop
- **Schedule teams** — Assign musicians and track availability
- **Export presentations** — Generate files for FreeShow, Quelea, or PDF handouts

---

## Installation

### Requirements

- A computer with [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- 5 minutes of your time

### Step 1: Download Javya

Open a terminal and run:

```bash
git clone https://github.com/ajhermosilla/javya.git
cd javya
```

### Step 2: Start the Application

```bash
docker compose up -d
```

Wait about 30 seconds for everything to start.

### Step 3: Open in Browser

Go to **http://localhost:5173**

---

## First-Time Setup

### Create Your Admin Account

1. Click **"Create Account"**
2. Enter your name, email, and password
3. Click **"Register"**

**Important:** The first account automatically becomes the **Admin**. This account can manage all users and settings.

### Invite Your Team

Once logged in as Admin:

1. Share the registration link with your team members
2. They create their own accounts
3. Go to the Users section to upgrade team leaders to the "Leader" role

**Role Permissions:**
| Role | Can Do |
|------|--------|
| Admin | Everything, including managing users |
| Leader | Create/delete songs and setlists, assign team members |
| Member | View and edit songs, mark personal availability |

---

## Adding Songs

### Create a Song Manually

1. Click **"Songs"** in the sidebar
2. Click **"Add Song"**
3. Fill in the details:
   - **Name** (required)
   - **Artist** (optional)
   - **Key** — Original and preferred keys for your team
   - **Tempo** — BPM for reference
   - **Mood & Themes** — For filtering later
   - **Lyrics** — Plain text lyrics
   - **ChordPro Chart** — Chords inline with lyrics
   - **URL** — Link to YouTube, Spotify, etc.
4. Click **"Save"**

### Import Songs from Files

Already have songs in ChordPro, OpenSong, or OpenLyrics format?

1. Click **"Songs"** → **"Import"**
2. Drag and drop your files (up to 20 at a time)
3. Review the parsed results
4. Select which songs to import
5. Click **"Import Selected"**

**Supported formats:**
- ChordPro (.cho, .crd, .chopro)
- OpenLyrics (.xml)
- OpenSong (.xml)
- Plain text (.txt)

---

## Building Setlists

### Create a Setlist

1. Click **"Setlists"** in the sidebar
2. Click **"Create Setlist"**
3. Enter:
   - **Name** — e.g., "Sunday Morning - January 12"
   - **Date** — Service date
   - **Event Type** — Sunday service, Wednesday, Special, etc.
4. Click **"Create"**

### Add Songs to a Setlist

1. Open the setlist
2. Click **"Edit"**
3. Search for songs and click to add them
4. **Drag and drop** to reorder
5. Click **"Save"**

### Export for Projection Software

1. Open the setlist
2. Click **"Export"**
3. Choose your format:
   - **FreeShow** (.project) — For FreeShow presentation software
   - **Quelea** (.qsch) — For Quelea church projection
   - **PDF Summary** — Song list for printing
   - **PDF Chords** — Chord charts for musicians

---

## Team Scheduling

### Set Your Availability

1. Click **"Availability"** in the sidebar
2. Click on calendar dates to mark yourself as:
   - **Available** (green)
   - **Unavailable** (red)
   - **Tentative** (yellow)
3. Add notes if needed (e.g., "Available after 10am")

### Set Recurring Patterns

Don't want to mark every Sunday individually?

1. Click **"Add Pattern"**
2. Choose:
   - **Day** — Sunday, Wednesday, etc.
   - **Frequency** — Weekly, biweekly, monthly
   - **Status** — Available, unavailable, tentative
   - **Date Range** — When this pattern applies
3. Click **"Save Pattern"**

### Assign Team Members (Leaders/Admins)

1. Click **"Scheduling"** in the sidebar
2. Click on a setlist in the calendar
3. Click **"Add Assignment"**
4. Select:
   - **Team Member**
   - **Role** — Worship leader, vocalist, guitarist, etc.
5. Team members will see their assignments and can confirm

---

## Tips for Worship Leaders

### Organize Your Song Library

Use **moods** and **themes** to categorize songs:

- **Moods**: Joyful, Reflective, Peaceful, Energetic...
- **Themes**: Worship, Communion, Opening, Thanksgiving...

Then filter songs when building setlists to find the right fit.

### Use ChordPro Format

For chord charts, use ChordPro format:

```
[G]Amazing [C]grace, how [G]sweet the sound
That [G]saved a [D]wretch like [G]me
```

This displays chords inline with lyrics and enables transposition.

### Keep Reference Links

Add YouTube or Spotify links to songs so team members can quickly reference the original version during practice.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Esc` | Close modal/dialog |
| Drag handles | Reorder songs in setlist |

---

## Language Settings

Javya supports English and Spanish.

1. Click the language icon in the top-right corner
2. Select your preferred language

---

## Getting Help

### Common Questions

**Q: How do I reset my password?**
A: Currently, ask your admin to create a new account. Password reset is coming soon.

**Q: Can I use this on my phone?**
A: Yes, the interface is mobile-friendly. Full mobile app coming in a future version.

**Q: Is my data backed up?**
A: Data is stored in a PostgreSQL database. Set up regular database backups for production use.

### Need More Help?

- **Technical issues:** [GitHub Issues](https://github.com/ajhermosilla/javya/issues)
- **Feature requests:** [GitHub Discussions](https://github.com/ajhermosilla/javya/discussions)

---

## What's Next?

Check out the [Roadmap](../ROADMAP.md) for upcoming features:

- Song transposition
- Email notifications
- Dashboard analytics
- Calendar integrations
- Mobile app

---

<p align="center">
  <i>Javy'a — Let us rejoice together</i>
</p>
