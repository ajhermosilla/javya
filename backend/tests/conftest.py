import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app

# Test database URL - uses a separate test database
# Uses 'db' hostname (Docker network) when running inside container
import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://javya:change_me_in_production@db:5432/javya_test"
)

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_maker() as session:
        yield session

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_song_data() -> dict[str, Any]:
    """Sample song data for testing."""
    return {
        "name": "Amazing Grace",
        "artist": "John Newton",
        "url": "https://www.youtube.com/watch?v=12345",
        "original_key": "G",
        "preferred_key": "E",
        "tempo_bpm": 72,
        "mood": "Reflective",
        "themes": ["Grace", "Salvation"],
        "lyrics": "Amazing grace, how sweet the sound\nThat saved a wretch like me",
        "chordpro_chart": "[G]Amazing [G7]grace, how [C]sweet the [G]sound",
        "min_band": ["acoustic guitar", "vocals"],
        "notes": "Great for communion service",
    }


@pytest.fixture
def sample_song_data_minimal() -> dict[str, Any]:
    """Minimal song data (only required fields)."""
    return {
        "name": "Simple Song",
    }
