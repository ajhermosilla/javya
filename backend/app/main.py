from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, songs, setlists, users, availability

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
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(songs.router, prefix="/api/v1/songs", tags=["songs"])
app.include_router(setlists.router, prefix="/api/v1/setlists", tags=["setlists"])
app.include_router(availability.router, prefix="/api/v1", tags=["availability"])


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
