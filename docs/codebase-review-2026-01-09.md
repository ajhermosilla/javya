# Codebase Review Report
**Date:** January 9, 2026

## Overview

Comprehensive review of the Javya codebase covering security, code quality, error handling, type safety, API consistency, database, test coverage, configuration, dependencies, and frontend issues.

**Total Issues Found: 35**
- 2 Critical
- 3 High
- 10 Medium
- 20 Low

---

## Critical Priority

### 1.1 Default/Placeholder Secrets in Configuration
**Files:**
- `backend/app/config.py:12`
- `.env.example:11-12,20`
- `docker-compose.yml:10,31`

**Issues:**
- Default `SECRET_KEY = "generate_a_random_secret_key_here"` is a placeholder
- Default `POSTGRES_PASSWORD = "change_me_in_production"` in config and docker-compose
- Database credentials hardcoded with default values

**Fix:** Generate unique secrets at deployment, use secrets management

---

### 1.2 DEBUG Mode Enabled by Default
**File:** `backend/app/config.py:11`

```python
debug: bool = True  # Default is True
```

**Issues:**
- Defaults to `True` which exposes SQLAlchemy query logs
- Detailed error messages exposed to clients in production

**Fix:** Default to `False`, only enable with explicit environment variable

---

## High Priority

### 2.1 CORS Configuration Too Permissive
**File:** `backend/app/main.py:16-22`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issues:**
- `allow_methods=["*"]` and `allow_headers=["*"]` are overly permissive
- `allow_credentials=True` with permissive settings is a security risk

**Fix:** Specify exact allowed methods and headers

---

### 2.2 Uvicorn Running in Auto-Reload Mode in Docker
**File:** `docker-compose.yml:40`

```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Issues:**
- `--reload` watches for file changes continuously
- High CPU usage in containers
- Not suitable for production

**Fix:** Create separate dev/prod configs, remove `--reload` for production

---

### 2.3 Missing Security Headers
**File:** `backend/app/main.py`

**Missing:**
- Content-Security-Policy (CSP)
- X-Content-Type-Options
- X-Frame-Options
- Strict-Transport-Security (HSTS)

**Fix:** Add security middleware for standard security headers

---

## Medium Priority

### 3.1 Inconsistent Error Response Format
**Files:**
- `frontend/src/api/client.ts:71`
- `frontend/src/api/auth.ts:13,32`

```typescript
// client.ts
throw new ApiError(response.status, error.detail || 'Request failed');

// auth.ts
throw new Error(error.detail || 'Registration failed');
```

**Issues:**
- Mixing `ApiError` and `Error` classes
- Inconsistent error type handling

**Fix:** Always use `ApiError` from client.ts

---

### 3.2 Silent Error Handling in Duplicate Check
**File:** `frontend/src/components/SongForm.tsx:83-95`

```typescript
try {
  const response = await songsApi.checkDuplicates([...]);
  // ...
} catch {
  // If duplicate check fails, proceed with creation
}
```

**Issues:**
- Silent catch block - errors completely ignored
- User has no feedback if duplicate check fails

**Fix:** Log error and optionally warn user

---

### 3.3 Unhandled Promise in Async Effect
**File:** `frontend/src/pages/SchedulingPage.tsx:61-73`

**Issues:**
- No cleanup function for component unmounting
- State update on unmounted component possible

**Fix:** Add abort controller for cleanup

---

### 3.4 Missing Database Indexes
**Files:**
- `backend/app/models/availability.py`
- `backend/app/models/setlist.py`

**Missing Indexes:**
- `Availability` user_id + date compound index
- `SetlistAssignment` user_id index
- `SetlistSong` position index

**Fix:** Add compound indexes for frequently queried combinations

---

### 3.5 Code Duplication in SQL Escaping
**Files:**
- `backend/app/routers/songs.py:20-22`
- `backend/app/routers/setlists.py:40-42`

```python
def escape_like_pattern(value: str) -> str:
    """Escape special LIKE pattern characters."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
```

**Fix:** Move to shared `app/utils/` module

---

### 3.6 No Frontend Health Check
**File:** `docker-compose.yml:42-56`

**Issues:**
- Backend has health check
- Frontend has no health check

**Fix:** Add health check endpoint for frontend

---

### 3.7 Frontend Docker Image Not Optimized
**File:** `frontend/Dockerfile`

**Issues:**
- No multi-stage build
- Dev dependencies included in final image
- No minification optimization

**Fix:** Use multi-stage build with production optimizations

---

### 3.8 Outdated Dependencies
**File:** `backend/requirements.txt`

**Issues:**
- `passlib==1.7.4` is from 2016
- No automated dependency update checking

**Fix:** Review and update dependencies

---

### 3.9 No Error Logging in Frontend
**File:** `frontend/src/pages/SchedulingPage.tsx:69`

```typescript
.catch((err) => {
  console.error(err);
  setUsersError(t('scheduling.usersLoadError'));
});
```

**Issues:**
- No structured error logging
- Error details lost in production

**Fix:** Implement proper error logging service

---

### 3.10 Empty Catch Block in Auth Context
**File:** `frontend/src/contexts/AuthContext.tsx:39`

```typescript
try {
  const userData = await authApi.getCurrentUser(token);
  setUser(userData);
} catch {
  clearStoredToken();
}
```

**Issues:**
- No error logging
- All errors treated the same

**Fix:** Add error logging, differentiate error types

---

## Low Priority

### 4.1 Debug Code Left in Production
**File:** `frontend/src/pages/SchedulingPage.tsx:95`

```typescript
console.log('Date clicked:', date);
```

**Fix:** Remove debug logging

---

### 4.2 Duplicate Type Definition
**File:** `frontend/src/pages/SchedulingPage.tsx:33-37`

```typescript
interface User {
  id: string;
  name: string;
  email: string;
}
```

**Fix:** Import from `../types/user`

---

### 4.3 Unused Parameter in Scheduling Endpoints
**Files:**
- `backend/app/routers/scheduling.py:29`
- `backend/app/routers/scheduling.py:80`

```python
current_user: Annotated[User, Depends(get_current_active_user)] = None,
```

**Fix:** Remove if not needed, or use for filtering

---

### 4.4 Inefficient Object Expiration
**File:** `backend/app/routers/setlists.py:183`

```python
db.expire_all()
```

**Fix:** Only expire specific object: `db.expire(setlist)`

---

### 4.5 Type Mismatch in Test
**File:** `frontend/src/utils/transpose.test.ts:522`

```typescript
expect(transposeChordPro(input, null as unknown as string, 'C')).toBe(input);
```

**Fix:** Use proper types or optional parameters

---

### 4.6 Race Condition in First User Registration
**File:** `backend/app/routers/auth.py:33-37`

```python
count_result = await db.execute(select(func.count()).select_from(User))
user_count = count_result.scalar()
role = UserRole.ADMIN if user_count == 0 else UserRole.MEMBER
```

**Issues:**
- Race condition between count check and insert
- Could result in multiple admins

**Fix:** Use database-level transactions or advisory locks

---

### 4.7 Token Redirection Security
**File:** `frontend/src/api/client.ts:63-68`

```typescript
if (response.status === 401) {
  clearStoredToken();
  if (!window.location.pathname.includes('/login')) {
    window.location.href = '/login';
  }
}
```

**Fix:** Use React Router's programmatic navigation

---

### 4.8 Missing Input Validation for URL Field
**File:** `backend/app/schemas/song.py:22`

```python
url: str | None = Field(None, max_length=500)
```

**Fix:** Use `HttpUrl` from pydantic for validation

---

### 4.9 Hardcoded Pagination Limits
**Files:**
- `backend/app/routers/songs.py:67-68`
- `backend/app/routers/users.py:21-22`
- `backend/app/routers/setlists.py:93-94`

**Fix:** Make configurable via settings

---

### 4.10 No Input Debouncing for Search
**File:** `frontend/src/components/SearchBar.tsx`

**Fix:** Add debounce for search input

---

### 4.11 Missing Cleanup in Auth Context Effect
**File:** `frontend/src/contexts/AuthContext.tsx:46-48`

**Fix:** Add abort controller for async operation

---

### 4.12 No Loading State in Some Components
**Files:**
- `SetlistAssignmentEditor` - no loading state during save
- `ImportModal` - no progress indicator

**Fix:** Add loading indicators

---

### 4.13 Test Database Not Isolated
**File:** `.github/workflows/ci.yml:20`

**Fix:** Add cleanup between test jobs

---

### 4.14-4.20 Additional Minor Issues
- Bool comparison style in `availability.py:159`
- Inconsistent API response models
- No security headers library
- Various minor type issues

---

## Summary by Category

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Security | 2 | 2 | 0 | 2 |
| Code Quality | 0 | 0 | 2 | 5 |
| Error Handling | 0 | 0 | 4 | 0 |
| Type Safety | 0 | 0 | 0 | 2 |
| API Consistency | 0 | 0 | 0 | 3 |
| Database | 0 | 0 | 1 | 2 |
| Test Coverage | 0 | 0 | 0 | 2 |
| Configuration | 0 | 1 | 2 | 0 |
| Dependencies | 0 | 0 | 1 | 1 |
| Frontend | 0 | 0 | 0 | 3 |

---

## Recommended Fix Order

### Phase 1: Security (Critical/High)
1. Generate real secrets for production
2. Set `debug: bool = False` as default
3. Restrict CORS configuration
4. Add security headers middleware
5. Create production Docker config

### Phase 2: Code Quality (Medium)
1. Centralize error handling in frontend
2. Add database indexes
3. Extract shared utilities
4. Add abort controllers to async effects

### Phase 3: Polish (Low)
1. Remove debug logging
2. Fix type issues
3. Add loading states
4. Implement search debouncing
