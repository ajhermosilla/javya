# User Testing Guide — Javya v0.7

This guide provides comprehensive test scenarios for validating Javya before the v0.7 release. The goal is to discover bugs, UX issues, and edge cases through systematic testing.

---

## Prerequisites

### Environment Setup
```bash
# Start all services
docker compose up -d

# Verify services are running
docker compose ps
```

| Service | URL | Expected |
|---------|-----|----------|
| Frontend | http://localhost:5173 | Login page |
| Backend API | http://localhost:8000 | `{"message":"Javya API"}` |
| API Docs | http://localhost:8000/docs | Swagger UI |

### Test Accounts
Create these accounts during testing (first user becomes admin):

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| Admin | admin@test.com | Test123! | Full access |
| Leader | leader@test.com | Test123! | Team management |
| Member | member@test.com | Test123! | Limited access |

---

## Test Session Checklist

Use this checklist to track your progress. Mark items with:
- ✅ Passed
- ❌ Failed (note the issue)
- ⚠️ Works but has UX issues

---

## 1. Authentication & Authorization

### 1.1 Registration
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 1.1.1 | First user registration | Go to /login, click "Register", fill form | Account created as Admin role | |
| 1.1.2 | Second user registration | Register another account | Account created as Member role | |
| 1.1.3 | Duplicate email | Try registering with existing email | Error message shown | |
| 1.1.4 | Invalid email format | Enter "notanemail" as email | Validation error | |
| 1.1.5 | Short password | Enter password < 6 chars | Validation error | |
| 1.1.6 | Empty fields | Submit with empty fields | Validation errors shown | |

### 1.2 Login
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 1.2.1 | Valid login | Enter correct credentials | Redirected to songs page | |
| 1.2.2 | Wrong password | Enter wrong password | Error message | |
| 1.2.3 | Non-existent user | Enter unregistered email | Error message | |
| 1.2.4 | Session persistence | Login, close tab, reopen | Still logged in | |
| 1.2.5 | Logout | Click logout in sidebar | Redirected to login | |

### 1.3 Role-Based Access
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 1.3.1 | Admin sees all users | Login as admin, go to user management | All users visible | |
| 1.3.2 | Admin changes role | Change member to leader | Role updated | |
| 1.3.3 | Leader cannot change roles | Login as leader | Role change option hidden/disabled | |
| 1.3.4 | Member limited access | Login as member | Cannot delete songs/setlists | |

---

## 2. Song Management

### 2.1 Create Songs
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 2.1.1 | Create basic song | Click "Add Song", fill name only | Song created | |
| 2.1.2 | Create full song | Fill all fields (name, artist, key, mood, themes, lyrics) | Song created with all data | |
| 2.1.3 | Create with ChordPro | Add ChordPro chart with [C], [Am], etc. | Chords parsed correctly | |
| 2.1.4 | Invalid BPM | Enter BPM < 20 or > 300 | Validation error | |
| 2.1.5 | Invalid URL | Enter "not a url" | Validation error | |
| 2.1.6 | Duplicate detection | Create song with same name+artist | Warning shown | |

### 2.2 Search & Filter
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 2.2.1 | Search by name | Type partial song name | Matching songs shown | |
| 2.2.2 | Search debounce | Type quickly | Only one search after typing stops | |
| 2.2.3 | Filter by key | Select a key from dropdown | Only songs in that key | |
| 2.2.4 | Filter by mood | Select a mood | Only songs with that mood | |
| 2.2.5 | Filter by theme | Select a theme | Only songs with that theme | |
| 2.2.6 | Combined filters | Search + key + mood | Intersection of all filters | |
| 2.2.7 | Clear filters | Clear all filters | All songs shown | |
| 2.2.8 | No results | Search for "xyznonexistent" | "No songs found" message | |

### 2.3 Edit & Delete Songs
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 2.3.1 | Edit song | Click edit, change name, save | Changes persisted | |
| 2.3.2 | Cancel edit | Make changes, click cancel | Original data preserved | |
| 2.3.3 | Delete song (admin) | Click delete as admin | Song removed | |
| 2.3.4 | Delete song (member) | Try delete as member | Not allowed | |

### 2.4 Song Detail View
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 2.4.1 | View lyrics | Click on song card | Lyrics displayed | |
| 2.4.2 | View ChordPro | Song with chords | Chords highlighted/formatted | |
| 2.4.3 | Song metadata | Check key, BPM, mood display | All metadata shown correctly | |

---

## 3. Song Transposition (v0.6 feature)

### 3.1 Transpose Chords
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 3.1.1 | Transpose up | Song in C, transpose to D | All chords shifted +2 semitones | |
| 3.1.2 | Transpose down | Song in G, transpose to E | All chords shifted -3 semitones | |
| 3.1.3 | Sharp to flat | Transpose C# to Db | Enharmonic equivalent shown | |
| 3.1.4 | Complex chords | Song with Am7, Cmaj7, Dsus4 | Extensions preserved | |
| 3.1.5 | Capo suggestion | Transpose far from original | Capo alternative suggested | |
| 3.1.6 | Reset to original | After transposing, reset | Original key restored | |

---

## 4. Song Import (v0.6 + v0.7 features)

### 4.1 File Import
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 4.1.1 | Import ChordPro | Upload .cho file | Parsed with chords | |
| 4.1.2 | Import OpenLyrics | Upload .xml OpenLyrics | Parsed correctly | |
| 4.1.3 | Import OpenSong | Upload OpenSong XML | Parsed correctly | |
| 4.1.4 | Import OnSong | Upload .onsong file | Parsed with metadata | |
| 4.1.5 | Import plain text | Upload .txt file | Basic parsing | |
| 4.1.6 | Import Ultimate Guitar | Upload UG format | Chords extracted | |
| 4.1.7 | Invalid file | Upload .jpg or .pdf | Error message | |
| 4.1.8 | Large file | Upload file > 1MB | Error or handled gracefully | |

### 4.2 ZIP Archive Import (v0.7)
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 4.2.1 | Import ZIP | Upload .zip with multiple songs | All songs in preview | |
| 4.2.2 | Mixed formats in ZIP | ZIP with .cho, .xml, .txt | Each parsed by format | |
| 4.2.3 | Nested folders in ZIP | ZIP with subdirectories | All files found | |
| 4.2.4 | Large ZIP | ZIP with 50+ songs | All parsed (may take time) | |
| 4.2.5 | ZIP > 200MB | Very large archive | Rejected with message | |
| 4.2.6 | ZIP > 1000 files | Archive with many files | Limited to 1000 | |

### 4.3 URL Import (v0.7)
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 4.3.1 | Import from URL | Paste URL to song page | Content fetched and parsed | |
| 4.3.2 | Invalid URL | Paste "not a url" | Validation error | |
| 4.3.3 | URL timeout | Paste slow/unreachable URL | Timeout error (10s) | |
| 4.3.4 | URL > 1MB | Page larger than limit | Error message | |

### 4.4 Clipboard Paste (v0.7)
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 4.4.1 | Paste lyrics | Paste text into import modal | Text parsed | |
| 4.4.2 | Paste ChordPro | Paste ChordPro format | Chords detected | |
| 4.4.3 | Paste with metadata | Text with "Title: X" header | Metadata extracted | |

### 4.5 Import Preview & Edit (v0.7)
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 4.5.1 | Preview before import | Upload file | Preview shown before saving | |
| 4.5.2 | Edit in preview | Change title in preview | Modified value saved | |
| 4.5.3 | Select songs to import | Multi-file import, deselect some | Only selected imported | |
| 4.5.4 | Duplicate warning | Import existing song | Warning shown | |
| 4.5.5 | Cancel import | Click cancel in preview | Nothing saved | |

### 4.6 Key Detection (v0.7)
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 4.6.1 | Detect key from chords | Import song with [G] [C] [D] | Key detected as G | |
| 4.6.2 | Minor key detection | Song with [Am] [Dm] [E] | Key detected as Am | |
| 4.6.3 | No chords | Plain lyrics | No key suggested | |

---

## 5. Setlist Management

### 5.1 Create Setlist
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 5.1.1 | Create empty setlist | Fill name and date only | Setlist created | |
| 5.1.2 | Create with songs | Add songs during creation | Songs attached | |
| 5.1.3 | Create with event type | Select Sunday Service, etc. | Event type saved | |
| 5.1.4 | Past date | Select date in the past | Allowed (for archiving) | |

### 5.2 Drag-and-Drop Ordering
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 5.2.1 | Reorder songs | Drag song to new position | Order updated | |
| 5.2.2 | Drag to top | Drag song to first position | Song now first | |
| 5.2.3 | Drag to bottom | Drag song to last position | Song now last | |
| 5.2.4 | Rapid reordering | Quickly drag multiple times | All changes saved | |
| 5.2.5 | Touch/mobile drag | On mobile device | Drag works (or graceful fallback) | |

### 5.3 Edit Setlist
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 5.3.1 | Add song to existing | Open setlist, add song | Song added at end | |
| 5.3.2 | Remove song | Click remove on song | Song removed | |
| 5.3.3 | Change setlist name | Edit name, save | Name updated | |
| 5.3.4 | Add song notes | Add notes to song in setlist | Notes saved per-song | |

### 5.4 Search & Filter Setlists
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 5.4.1 | Search by name | Type setlist name | Matching setlists shown | |
| 5.4.2 | Filter by event type | Select event type | Only matching type | |
| 5.4.3 | No results | Search nonexistent | "No setlists found" | |

---

## 6. Export Features

### 6.1 FreeShow Export
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 6.1.1 | Export setlist | Click FreeShow export | .project file downloaded | |
| 6.1.2 | Import in FreeShow | Open file in FreeShow | Songs appear correctly | |
| 6.1.3 | Section slides | Song with [Verse], [Chorus] | Separate slides per section | |
| 6.1.4 | Special characters | Song with accents (é, ñ) | Characters preserved | |

### 6.2 Quelea Export
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 6.2.1 | Export setlist | Click Quelea export | .qsch file downloaded | |
| 6.2.2 | Import in Quelea | Open file in Quelea | Songs appear correctly | |
| 6.2.3 | Song metadata | Check title, artist, key | Metadata included | |

### 6.3 PDF Export
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 6.3.1 | Export summary | Export PDF summary | List of songs with details | |
| 6.3.2 | Export chord charts | Export chord chart PDF | Chords visible in output | |
| 6.3.3 | Print PDF | Print the exported PDF | Prints correctly | |
| 6.3.4 | Long setlist | 10+ songs | All songs in PDF | |

---

## 7. Availability Calendar

### 7.1 Set Availability
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 7.1.1 | Mark available | Click date, select "Available" | Green indicator | |
| 7.1.2 | Mark unavailable | Click date, select "Unavailable" | Red indicator | |
| 7.1.3 | Mark maybe | Click date, select "Maybe" | Yellow indicator | |
| 7.1.4 | Add note | Add note to availability | Note saved | |
| 7.1.5 | Clear availability | Remove availability | Date cleared | |
| 7.1.6 | Past dates | Try setting past date | Should work (or be disabled) | |

### 7.2 Recurring Patterns
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 7.2.1 | Weekly pattern | Set "Every Sunday available" | Sundays marked | |
| 7.2.2 | Biweekly pattern | Set every other week | Alternating weeks marked | |
| 7.2.3 | Monthly pattern | Set first Sunday of month | Monthly dates marked | |
| 7.2.4 | Pattern with end date | Set pattern ending in 3 months | Pattern stops at end date | |
| 7.2.5 | Override pattern | Pattern exists, override one date | Override takes precedence | |
| 7.2.6 | Delete pattern | Remove recurring pattern | Future dates cleared | |

### 7.3 Team Availability (Leader/Admin)
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 7.3.1 | View team | As leader, view team availability | All members visible | |
| 7.3.2 | Filter by date | Select date range | Only that range shown | |
| 7.3.3 | Member cannot view | As member, try team view | Access denied or hidden | |

---

## 8. Team Scheduling

### 8.1 Calendar View
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 8.1.1 | View calendar | Go to scheduling page | Calendar with setlists | |
| 8.1.2 | Navigate months | Click next/previous month | Month changes | |
| 8.1.3 | Click setlist | Click setlist on calendar | Setlist details shown | |

### 8.2 Assignments
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 8.2.1 | Assign member | As leader, assign member to role | Assignment created | |
| 8.2.2 | Multiple roles | Assign same person to 2 roles | Both assignments saved | |
| 8.2.3 | All service roles | Test each role (worship leader, vocalist, etc.) | All 8 roles work | |
| 8.2.4 | Add assignment notes | Add notes to assignment | Notes saved | |
| 8.2.5 | Remove assignment | Delete an assignment | Assignment removed | |
| 8.2.6 | Member cannot assign | As member, try to assign | Not allowed | |

### 8.3 Confirmation Workflow
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 8.3.1 | Confirm assignment | As assigned member, confirm | Status changed to confirmed | |
| 8.3.2 | Decline assignment | Unconfirm an assignment | Status changed to unconfirmed | |
| 8.3.3 | View my assignments | Check "My Assignments" | Only own assignments shown | |
| 8.3.4 | Confirm others' | Try confirming someone else's | Not allowed | |

---

## 9. Internationalization (i18n)

### 9.1 Language Switching
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 9.1.1 | Switch to Spanish | Click language switcher, select ES | All UI in Spanish | |
| 9.1.2 | Switch to English | Click language switcher, select EN | All UI in English | |
| 9.1.3 | Language persistence | Switch language, refresh page | Language preserved | |
| 9.1.4 | All pages translated | Navigate all pages in Spanish | No English strings | |

### 9.2 Content in Different Languages
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 9.2.1 | Spanish song names | Create song with "Señor" | Accents displayed correctly | |
| 9.2.2 | Special characters | Song with ñ, é, ü, etc. | All characters work | |

---

## 10. Error Handling & Edge Cases

### 10.1 Network Errors
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 10.1.1 | Backend down | Stop backend, try action | Error message shown | |
| 10.1.2 | Slow network | Throttle network (DevTools) | Loading states work | |
| 10.1.3 | Request timeout | Very slow response | Timeout handled gracefully | |

### 10.2 Session Handling
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 10.2.1 | Expired token | Wait for token expiry (7 days) or invalidate | Redirected to login | |
| 10.2.2 | Multiple tabs | Open app in multiple tabs | Both work independently | |
| 10.2.3 | Logout in one tab | Logout in tab A, use tab B | Tab B handles gracefully | |

### 10.3 Data Edge Cases
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 10.3.1 | Very long song name | 500+ character name | Truncated or handled | |
| 10.3.2 | Very long lyrics | 10,000+ character lyrics | Saved and displayed | |
| 10.3.3 | Empty setlist export | Export setlist with 0 songs | Handled gracefully | |
| 10.3.4 | Unicode everywhere | Emojis, Chinese, Arabic in names | All work correctly | |
| 10.3.5 | SQL injection attempt | Try `'; DROP TABLE songs;--` | Safely escaped | |
| 10.3.6 | XSS attempt | Try `<script>alert('xss')</script>` | Safely escaped | |

### 10.4 Concurrent Edits
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 10.4.1 | Two users edit song | User A and B edit same song | Last save wins (or conflict shown) | |
| 10.4.2 | Delete while editing | User A edits, User B deletes | Error handled | |

---

## 11. UI/UX Review

### 11.1 Visual Consistency
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 11.1.1 | Button styles | Check all buttons | Consistent styling | |
| 11.1.2 | Form styles | Check all forms | Consistent inputs | |
| 11.1.3 | Color scheme | Review all pages | Consistent colors | |
| 11.1.4 | Typography | Check fonts and sizes | Consistent typography | |
| 11.1.5 | Spacing | Check margins/padding | Consistent spacing | |

### 11.2 Responsiveness
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 11.2.1 | Desktop (1920px) | View on large monitor | Layout works | |
| 11.2.2 | Laptop (1366px) | View on laptop | Layout adapts | |
| 11.2.3 | Tablet (768px) | View on iPad | Usable layout | |
| 11.2.4 | Mobile (375px) | View on phone | Mobile layout | |
| 11.2.5 | Sidebar collapse | On small screens | Sidebar collapses | |

### 11.3 Navigation
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 11.3.1 | All sidebar links | Click each menu item | Correct page loads | |
| 11.3.2 | Browser back/forward | Use browser navigation | Works correctly | |
| 11.3.3 | Direct URL access | Type URL directly | Page loads (if authorized) | |
| 11.3.4 | 404 handling | Go to /nonexistent | 404 page or redirect | |

### 11.4 Feedback & States
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 11.4.1 | Loading indicators | Slow actions | Spinner or skeleton shown | |
| 11.4.2 | Success messages | Create/edit/delete | Success feedback | |
| 11.4.3 | Error messages | Cause an error | Clear error message | |
| 11.4.4 | Empty states | Empty song list | "No songs" message | |
| 11.4.5 | Confirmation dialogs | Delete actions | "Are you sure?" prompt | |

---

## 12. Performance

### 12.1 Load Times
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 12.1.1 | Initial load | Clear cache, load app | < 3 seconds | |
| 12.1.2 | Song list (100 songs) | Load with many songs | < 2 seconds | |
| 12.1.3 | Large setlist | Setlist with 20 songs | < 2 seconds | |
| 12.1.4 | Import preview | Upload 50-song ZIP | < 10 seconds | |

### 12.2 Interactions
| # | Test Case | Steps | Expected | Status |
|---|-----------|-------|----------|--------|
| 12.2.1 | Search response | Type in search | Results within 500ms | |
| 12.2.2 | Drag-and-drop | Reorder songs | Smooth animation | |
| 12.2.3 | Modal opening | Open any modal | < 100ms delay | |

---

## Issue Reporting Template

When you find an issue, document it with this template:

```markdown
### Issue Title

**Severity:** Critical / High / Medium / Low
**Test Case:** #X.X.X
**Browser:** Chrome 120 / Firefox 121 / Safari 17
**Device:** Desktop / Mobile

**Steps to Reproduce:**
1. Go to...
2. Click on...
3. Enter...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happened

**Screenshot/Video:**
(Attach if helpful)

**Notes:**
Any additional context
```

---

## Post-Testing Summary

After completing all tests, summarize:

### Statistics
- Total tests: ___
- Passed: ___
- Failed: ___
- UX Issues: ___

### Critical Issues (must fix before release)
1.
2.

### High Priority Issues
1.
2.

### Medium Priority Issues
1.
2.

### Low Priority / Nice to Have
1.
2.

### UX Improvements Identified
1.
2.

---

## Sign-off

| Tester | Date | Version | Recommendation |
|--------|------|---------|----------------|
| | | v0.7-rc | Ready / Not Ready |

---

<p align="center">
  <i>Thank you for helping make Javya better!</i>
</p>
