"""Tests for duplicate song detection."""

import pytest
from httpx import AsyncClient

from app.models.song import Song


class TestCheckDuplicatesEndpoint:
    """Tests for POST /api/v1/songs/check-duplicates endpoint."""

    async def test_no_duplicates_found(self, client: AsyncClient, db_session):
        """Should return empty list when no duplicates exist."""
        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={
                "songs": [
                    {"name": "Unique Song", "artist": "Unique Artist"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["duplicates"] == []

    async def test_finds_exact_duplicate(
        self, client: AsyncClient, db_session
    ):
        """Should find exact match on name + artist."""
        # Create existing song
        existing = Song(name="Amazing Grace", artist="John Newton")
        db_session.add(existing)
        await db_session.commit()
        await db_session.refresh(existing)

        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={
                "songs": [
                    {"name": "Amazing Grace", "artist": "John Newton"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["duplicates"]) == 1
        assert data["duplicates"][0]["index"] == 0
        assert data["duplicates"][0]["name"] == "Amazing Grace"
        assert data["duplicates"][0]["existing_song"]["id"] == str(existing.id)

    async def test_case_insensitive_match(
        self, client: AsyncClient, db_session
    ):
        """Should match regardless of case."""
        existing = Song(name="Amazing Grace", artist="John Newton")
        db_session.add(existing)
        await db_session.commit()

        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={
                "songs": [
                    {"name": "AMAZING GRACE", "artist": "JOHN NEWTON"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["duplicates"]) == 1

    async def test_different_artist_not_duplicate(
        self, client: AsyncClient, db_session
    ):
        """Same song name with different artist is not a duplicate."""
        existing = Song(name="Amazing Grace", artist="John Newton")
        db_session.add(existing)
        await db_session.commit()

        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={
                "songs": [
                    {"name": "Amazing Grace", "artist": "Chris Tomlin"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["duplicates"] == []

    async def test_null_artist_matches_null(
        self, client: AsyncClient, db_session
    ):
        """Song with no artist matches other song with no artist."""
        existing = Song(name="Amazing Grace", artist=None)
        db_session.add(existing)
        await db_session.commit()

        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={
                "songs": [
                    {"name": "Amazing Grace", "artist": None},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["duplicates"]) == 1

    async def test_null_artist_does_not_match_with_artist(
        self, client: AsyncClient, db_session
    ):
        """Song with no artist does not match song with artist."""
        existing = Song(name="Amazing Grace", artist="John Newton")
        db_session.add(existing)
        await db_session.commit()

        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={
                "songs": [
                    {"name": "Amazing Grace", "artist": None},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["duplicates"] == []

    async def test_bulk_check_multiple_songs(
        self, client: AsyncClient, db_session
    ):
        """Should check multiple songs and return all duplicates."""
        # Create two existing songs
        song1 = Song(name="Amazing Grace", artist="John Newton")
        song2 = Song(name="How Great Is Our God", artist="Chris Tomlin")
        db_session.add_all([song1, song2])
        await db_session.commit()

        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={
                "songs": [
                    {"name": "Amazing Grace", "artist": "John Newton"},
                    {"name": "New Song", "artist": "New Artist"},
                    {"name": "How Great Is Our God", "artist": "Chris Tomlin"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["duplicates"]) == 2

        # Check indices are correct
        indices = [d["index"] for d in data["duplicates"]]
        assert 0 in indices
        assert 2 in indices

    async def test_empty_songs_list_rejected(
        self, client: AsyncClient, db_session
    ):
        """Should reject empty songs list."""
        response = await client.post(
            "/api/v1/songs/check-duplicates",
            json={"songs": []},
        )

        assert response.status_code == 422


class TestImportPreviewWithDuplicates:
    """Tests for duplicate detection in import preview."""

    async def test_preview_includes_duplicate_info(
        self, client: AsyncClient, db_session
    ):
        """Preview should include duplicate info for matching songs."""
        # Create existing song
        existing = Song(name="Amazing Grace", artist="John Newton", original_key="G")
        db_session.add(existing)
        await db_session.commit()
        await db_session.refresh(existing)

        # Create a ChordPro file with same song
        content = b"{title: Amazing Grace}\n{artist: John Newton}\n[G]Amazing grace"

        response = await client.post(
            "/api/v1/songs/import/preview",
            files=[("files", ("amazing.cho", content, "text/plain"))],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["successful"] == 1

        song = data["songs"][0]
        assert song["success"] is True
        assert song["duplicate"] is not None
        assert song["duplicate"]["id"] == str(existing.id)
        assert song["duplicate"]["name"] == "Amazing Grace"

    async def test_preview_no_duplicate_for_new_song(
        self, client: AsyncClient, db_session
    ):
        """Preview should have null duplicate for new songs."""
        content = b"{title: Brand New Song}\n{artist: New Artist}\n[G]Lyrics"

        response = await client.post(
            "/api/v1/songs/import/preview",
            files=[("files", ("new.cho", content, "text/plain"))],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["successful"] == 1

        song = data["songs"][0]
        assert song["success"] is True
        assert song["duplicate"] is None

    async def test_preview_case_insensitive_duplicate(
        self, client: AsyncClient, db_session
    ):
        """Preview should detect case-insensitive duplicates."""
        existing = Song(name="Amazing Grace", artist="John Newton")
        db_session.add(existing)
        await db_session.commit()

        # Use different case in file
        content = b"{title: AMAZING GRACE}\n{artist: john newton}\n[G]Lyrics"

        response = await client.post(
            "/api/v1/songs/import/preview",
            files=[("files", ("song.cho", content, "text/plain"))],
        )

        assert response.status_code == 200
        data = response.json()

        song = data["songs"][0]
        assert song["duplicate"] is not None


class TestDuplicateDetectorService:
    """Tests for the duplicate detector service directly."""

    async def test_find_duplicates_returns_correct_indices(
        self, db_session
    ):
        """Service should return correct indices for duplicates."""
        from app.schemas.duplicate import SongCheck
        from app.services.duplicate_detector import find_duplicates

        # Create existing song
        existing = Song(name="Test Song", artist="Test Artist")
        db_session.add(existing)
        await db_session.commit()

        songs = [
            SongCheck(name="Different Song", artist="Different Artist"),
            SongCheck(name="Test Song", artist="Test Artist"),
            SongCheck(name="Another Song", artist="Another Artist"),
        ]

        duplicates = await find_duplicates(db_session, songs)

        assert len(duplicates) == 1
        assert duplicates[0].index == 1
        assert duplicates[0].name == "Test Song"

    async def test_find_single_duplicate(self, db_session):
        """find_single_duplicate should return matching song."""
        from app.services.duplicate_detector import find_single_duplicate

        existing = Song(name="Test Song", artist="Test Artist")
        db_session.add(existing)
        await db_session.commit()

        # Should find duplicate
        result = await find_single_duplicate(db_session, "Test Song", "Test Artist")
        assert result is not None
        assert result.name == "Test Song"

        # Should not find with different artist
        result = await find_single_duplicate(db_session, "Test Song", "Other Artist")
        assert result is None

        # Should not find with different name
        result = await find_single_duplicate(db_session, "Other Song", "Test Artist")
        assert result is None
