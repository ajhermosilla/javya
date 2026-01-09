# Session Summary: 2025-01-08

## Feature: Smarter Parsing for Song Imports

### Overview
Implemented intelligent key detection from chord progressions and automatic section detection/normalization for the song import feature.

### Changes Made

#### Backend - Key Detection (`key_detector.py`)
- Created `KeyDetector` class using Circle of Fifths music theory
- Extracts root notes from complex chord names (Am7, D/F#, Cmaj7, etc.)
- Calculates fit scores for each candidate key based on chord function weights:
  - I (tonic): 3.0, V (dominant): 2.5, IV (subdominant): 2.0
  - vi: 1.5, ii/iii: 1.0, vii: 0.5
- Returns detected key with confidence level (high/medium/low)
- 28 unit tests covering various progressions and edge cases

#### Backend - Section Detection (`section_detector.py`)
- Created `SectionDetector` class for marker normalization
- Normalizes shorthand markers: `[V1]` → `[Verse 1]`, `[C]` → `[Chorus]`
- Heuristic detection when no markers exist:
  - Repeated blocks identified as choruses
  - Unique blocks treated as verses
- Supports all common section types: Verse, Chorus, Bridge, Pre-Chorus, Tag, Intro, Outro, Interlude, Instrumental
- 26 unit tests for marker patterns and heuristic detection

#### Backend - Parser Integration
Updated all 6 parsers to use the new detectors:
- `chordpro_parser.py`
- `onsong_parser.py`
- `opensong_parser.py`
- `openlyrics_parser.py`
- `ultimateguitar_parser.py`
- `plaintext_parser.py`

Each parser now:
1. Extracts chords from content
2. Detects key using `KeyDetector`
3. Normalizes sections using `SectionDetector`
4. Returns both specified key (from metadata) and detected key (from chords)

#### Backend - Schema Updates
- `ParseResult` dataclass: Added `specified_key`, `detected_key`, `key_confidence`, `sections_normalized`
- `ParsedSong` Pydantic model: Matching fields for API response

#### Frontend - KeyIndicator Component
- New component to display key detection results
- Shows single badge when keys match or only one exists
- Shows selection buttons when specified and detected keys differ
- Includes confidence badge (High/Med/Low)
- Styled with purple for detected, blue for specified, green for match

#### Frontend - Import Preview Updates
- Added "Key" column to the import preview table
- `KeyIndicator` component in each row
- Users can choose between specified and detected keys when they conflict
- Selected key is used when confirming import

#### Frontend - ImportModal Updates
- Added `keySelections` state to track user key choices
- `handleKeySelectionChange` handler for key selection
- Applies selected key to song data during import confirmation

#### i18n Translations
Added English and Spanish translations for:
- `import.preview.key` - Column header
- `import.keyConfidence.high/medium/low` - Confidence badges
- `import.keySource.specified/detected/file/chords` - Key source labels

### Files Created
| File | Purpose |
|------|---------|
| `backend/app/services/import_song/key_detector.py` | Key detection algorithm |
| `backend/app/services/import_song/section_detector.py` | Section detection/normalization |
| `backend/tests/test_key_detector.py` | 28 key detection tests |
| `backend/tests/test_section_detector.py` | 26 section detection tests |
| `frontend/src/components/KeyIndicator.tsx` | Key selection UI component |
| `frontend/src/components/KeyIndicator.css` | KeyIndicator styling |

### Files Modified
| File | Changes |
|------|---------|
| `backend/app/services/import_song/base.py` | Added detector instances and helper methods |
| `backend/app/schemas/import_song.py` | Added key/section fields to ParsedSong |
| `backend/app/routers/import_songs.py` | Pass new fields in response |
| `backend/app/services/import_song/*.py` | All 6 parsers updated |
| `frontend/src/types/import.ts` | Added TypeScript types |
| `frontend/src/components/ImportPreview.tsx` | Added Key column |
| `frontend/src/components/ImportPreview.css` | Key column styling |
| `frontend/src/components/ImportModal.tsx` | Key selection state management |
| `frontend/src/i18n/locales/en.json` | English translations |
| `frontend/src/i18n/locales/es.json` | Spanish translations |

### Test Results
- All 360 backend tests passing
- Frontend builds successfully
- CI pipeline passed

### Commits
1. `cceb156` - feat: add smart key detection and section normalization for imports

### Algorithm Details

#### Key Detection Algorithm
```
1. Extract root notes from all chords
2. Count frequency of each root note
3. For each candidate key (0-11 semitones):
   - Calculate weighted score based on chord functions
   - Chords in the key get positive weight
   - Non-diatonic chords get negative weight
4. Highest scoring key wins
5. Confidence = margin between best and second-best candidate
```

#### Section Detection Algorithm
```
1. Check for existing markers using regex
2. If markers found:
   - Normalize format (V1 → Verse 1, C → Chorus)
   - Auto-number unnumbered sections
3. If no markers:
   - Split content into blocks by blank lines
   - Find repeated blocks (similarity >= 85%) → Chorus
   - Unique blocks → Verse
   - Add markers to normalized content
```

### Next Steps
- Consider adding relative minor key detection
- Could add time signature detection from rhythm patterns
- May add bridge/pre-chorus heuristics based on position and length
