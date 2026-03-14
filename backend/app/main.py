from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.middleware import SecurityHeadersMiddleware
from app.rate_limit import limiter
from app.routers import auth, songs, setlists, users, availability, scheduling, import_songs

app = FastAPI(
    title="Javya API",
    description="Open-source worship planning for church teams",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(songs.router, prefix="/api/v1/songs", tags=["songs"])
app.include_router(import_songs.router, prefix="/api/v1/songs/import", tags=["import"])
app.include_router(setlists.router, prefix="/api/v1/setlists", tags=["setlists"])
app.include_router(availability.router, prefix="/api/v1", tags=["availability"])
app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "javya-api"}


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Javya API",
        "version": "0.1.0",
        "description": "Open-source worship planning for church teams",
        "docs": "/docs",
    }
