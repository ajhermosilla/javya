from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient


async def get_admin_headers(client: AsyncClient) -> dict[str, str]:
    """Register first user (becomes admin) and return auth headers."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "admin@test.com", "name": "Admin", "password": "testpassword123"},
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCreateSong:
    """Tests for POST /api/v1/songs/ endpoint."""

    @pytest.mark.asyncio
    async def test_create_song_full(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test creating a song with all fields."""
        response = await client.post("/api/v1/songs/", json=sample_song_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_song_data["name"]
        assert data["artist"] == sample_song_data["artist"]
        assert data["url"] == sample_song_data["url"]
        assert data["original_key"] == sample_song_data["original_key"]
        assert data["preferred_key"] == sample_song_data["preferred_key"]
        assert data["tempo_bpm"] == sample_song_data["tempo_bpm"]
        assert data["mood"] == sample_song_data["mood"]
        assert data["themes"] == sample_song_data["themes"]
        assert data["lyrics"] == sample_song_data["lyrics"]
        assert data["chordpro_chart"] == sample_song_data["chordpro_chart"]
        assert data["min_band"] == sample_song_data["min_band"]
        assert data["notes"] == sample_song_data["notes"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_song_minimal(
        self, client: AsyncClient, sample_song_data_minimal: dict[str, Any]
    ) -> None:
        """Test creating a song with only required fields."""
        response = await client.post("/api/v1/songs/", json=sample_song_data_minimal)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_song_data_minimal["name"]
        assert data["artist"] is None
        assert data["url"] is None

    @pytest.mark.asyncio
    async def test_create_song_missing_name(self, client: AsyncClient) -> None:
        """Test that creating a song without name fails."""
        response = await client.post("/api/v1/songs/", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_song_invalid_key(self, client: AsyncClient) -> None:
        """Test that invalid musical key is rejected."""
        response = await client.post(
            "/api/v1/songs/",
            json={"name": "Test Song", "original_key": "Z"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_song_invalid_mood(self, client: AsyncClient) -> None:
        """Test that invalid mood is rejected."""
        response = await client.post(
            "/api/v1/songs/",
            json={"name": "Test Song", "mood": "InvalidMood"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_song_invalid_tempo(self, client: AsyncClient) -> None:
        """Test that invalid tempo (out of range) is rejected."""
        response = await client.post(
            "/api/v1/songs/",
            json={"name": "Test Song", "tempo_bpm": 500},
        )

        assert response.status_code == 422


class TestListSongs:
    """Tests for GET /api/v1/songs/ endpoint."""

    @pytest.mark.asyncio
    async def test_list_songs_empty(self, client: AsyncClient) -> None:
        """Test listing songs when database is empty."""
        response = await client.get("/api/v1/songs/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_songs_with_data(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test listing songs after creating some."""
        # Create two songs
        await client.post("/api/v1/songs/", json=sample_song_data)
        await client.post(
            "/api/v1/songs/", json={"name": "Second Song", "artist": "Another Artist"}
        )

        response = await client.get("/api/v1/songs/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_songs_search_by_name(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test searching songs by name."""
        await client.post("/api/v1/songs/", json=sample_song_data)
        await client.post("/api/v1/songs/", json={"name": "Different Song"})

        response = await client.get("/api/v1/songs/?search=amazing")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Amazing Grace"

    @pytest.mark.asyncio
    async def test_list_songs_search_by_artist(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test searching songs by artist."""
        await client.post("/api/v1/songs/", json=sample_song_data)

        response = await client.get("/api/v1/songs/?search=newton")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["artist"] == "John Newton"

    @pytest.mark.asyncio
    async def test_list_songs_filter_by_key(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test filtering songs by key."""
        await client.post("/api/v1/songs/", json=sample_song_data)
        await client.post(
            "/api/v1/songs/", json={"name": "D Song", "original_key": "D"}
        )

        # Filter by G (matches original_key)
        response = await client.get("/api/v1/songs/?key=G")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["original_key"] == "G"

        # Filter by E (matches preferred_key)
        response = await client.get("/api/v1/songs/?key=E")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["preferred_key"] == "E"

    @pytest.mark.asyncio
    async def test_list_songs_filter_by_mood(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test filtering songs by mood."""
        await client.post("/api/v1/songs/", json=sample_song_data)
        await client.post(
            "/api/v1/songs/", json={"name": "Joyful Song", "mood": "Joyful"}
        )

        response = await client.get("/api/v1/songs/?mood=Reflective")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["mood"] == "Reflective"

    @pytest.mark.asyncio
    async def test_list_songs_filter_by_theme(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test filtering songs by theme."""
        await client.post("/api/v1/songs/", json=sample_song_data)
        await client.post(
            "/api/v1/songs/", json={"name": "Worship Song", "themes": ["Worship"]}
        )

        response = await client.get("/api/v1/songs/?theme=Grace")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Grace" in data[0]["themes"]

    @pytest.mark.asyncio
    async def test_list_songs_pagination(self, client: AsyncClient) -> None:
        """Test pagination with skip and limit."""
        # Create 5 songs
        for i in range(5):
            await client.post("/api/v1/songs/", json={"name": f"Song {i}"})

        # Get first 2
        response = await client.get("/api/v1/songs/?limit=2")
        assert len(response.json()) == 2

        # Get next 2
        response = await client.get("/api/v1/songs/?skip=2&limit=2")
        assert len(response.json()) == 2

        # Get last 1
        response = await client.get("/api/v1/songs/?skip=4&limit=2")
        assert len(response.json()) == 1


class TestGetSong:
    """Tests for GET /api/v1/songs/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_song_success(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test getting a song by ID."""
        create_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/songs/{song_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == song_id
        assert data["name"] == sample_song_data["name"]

    @pytest.mark.asyncio
    async def test_get_song_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent song returns 404."""
        fake_id = str(uuid4())

        response = await client.get(f"/api/v1/songs/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_song_invalid_id(self, client: AsyncClient) -> None:
        """Test getting a song with invalid UUID format."""
        response = await client.get("/api/v1/songs/not-a-uuid")

        assert response.status_code == 422


class TestUpdateSong:
    """Tests for PUT /api/v1/songs/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_song_success(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test updating a song."""
        create_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = create_response.json()["id"]

        updated_data = sample_song_data.copy()
        updated_data["name"] = "Updated Amazing Grace"
        updated_data["tempo_bpm"] = 80

        response = await client.put(f"/api/v1/songs/{song_id}", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Amazing Grace"
        assert data["tempo_bpm"] == 80

    @pytest.mark.asyncio
    async def test_update_song_not_found(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test updating a non-existent song returns 404."""
        fake_id = str(uuid4())

        response = await client.put(f"/api/v1/songs/{fake_id}", json=sample_song_data)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_song_invalid_data(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test updating with invalid data fails."""
        create_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/songs/{song_id}",
            json={"name": "Test", "mood": "InvalidMood"},
        )

        assert response.status_code == 422


class TestDeleteSong:
    """Tests for DELETE /api/v1/songs/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_song_success(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test deleting a song (requires admin/leader auth)."""
        headers = await get_admin_headers(client)
        create_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/songs/{song_id}", headers=headers)

        assert response.status_code == 204

        # Verify song is deleted
        get_response = await client.get(f"/api/v1/songs/{song_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_song_not_found(self, client: AsyncClient) -> None:
        """Test deleting a non-existent song returns 404."""
        headers = await get_admin_headers(client)
        fake_id = str(uuid4())

        response = await client.delete(f"/api/v1/songs/{fake_id}", headers=headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_song_invalid_id(self, client: AsyncClient) -> None:
        """Test deleting with invalid UUID format."""
        headers = await get_admin_headers(client)
        response = await client.delete("/api/v1/songs/not-a-uuid", headers=headers)

        assert response.status_code == 422
