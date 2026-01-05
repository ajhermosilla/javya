from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError


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


class TestCreateSetlist:
    """Tests for POST /api/v1/setlists/ endpoint."""

    @pytest.mark.asyncio
    async def test_create_setlist_full(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test creating a setlist with all fields."""
        response = await client.post("/api/v1/setlists/", json=sample_setlist_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_setlist_data["name"]
        assert data["description"] == sample_setlist_data["description"]
        assert data["service_date"] == sample_setlist_data["service_date"]
        assert data["event_type"] == sample_setlist_data["event_type"]
        assert data["songs"] == []
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_setlist_minimal(
        self, client: AsyncClient, sample_setlist_data_minimal: dict[str, Any]
    ) -> None:
        """Test creating a setlist with only required fields."""
        response = await client.post("/api/v1/setlists/", json=sample_setlist_data_minimal)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_setlist_data_minimal["name"]
        assert data["description"] is None
        assert data["service_date"] is None
        assert data["event_type"] is None

    @pytest.mark.asyncio
    async def test_create_setlist_with_songs(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test creating a setlist with songs."""
        # First create some songs
        song1_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song1_id = song1_response.json()["id"]

        song2_response = await client.post(
            "/api/v1/songs/", json={"name": "Second Song", "lyrics": "Some lyrics"}
        )
        song2_id = song2_response.json()["id"]

        # Create setlist with songs
        setlist_data = {
            **sample_setlist_data,
            "songs": [
                {"song_id": song1_id, "position": 0, "notes": "Opening song"},
                {"song_id": song2_id, "position": 1},
            ],
        }
        response = await client.post("/api/v1/setlists/", json=setlist_data)

        assert response.status_code == 201
        data = response.json()
        assert len(data["songs"]) == 2
        assert data["songs"][0]["song"]["id"] == song1_id
        assert data["songs"][0]["notes"] == "Opening song"
        assert data["songs"][1]["song"]["id"] == song2_id

    @pytest.mark.asyncio
    async def test_create_setlist_missing_name(self, client: AsyncClient) -> None:
        """Test that creating a setlist without name fails."""
        response = await client.post("/api/v1/setlists/", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_setlist_whitespace_name(self, client: AsyncClient) -> None:
        """Test that whitespace-only name is rejected."""
        response = await client.post("/api/v1/setlists/", json={"name": "   "})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_setlist_invalid_event_type(self, client: AsyncClient) -> None:
        """Test that invalid event type is rejected."""
        response = await client.post(
            "/api/v1/setlists/",
            json={"name": "Test Setlist", "event_type": "InvalidType"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_setlist_invalid_song_id(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test that invalid song ID in songs list raises IntegrityError."""
        fake_song_id = str(uuid4())
        setlist_data = {
            **sample_setlist_data,
            "songs": [{"song_id": fake_song_id, "position": 0}],
        }

        # Should fail with integrity error (foreign key violation)
        with pytest.raises(IntegrityError):
            await client.post("/api/v1/setlists/", json=setlist_data)


class TestListSetlists:
    """Tests for GET /api/v1/setlists/ endpoint."""

    @pytest.mark.asyncio
    async def test_list_setlists_empty(self, client: AsyncClient) -> None:
        """Test listing setlists when database is empty."""
        response = await client.get("/api/v1/setlists/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_setlists_with_data(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test listing setlists after creating some."""
        await client.post("/api/v1/setlists/", json=sample_setlist_data)
        await client.post("/api/v1/setlists/", json={"name": "Second Setlist"})

        response = await client.get("/api/v1/setlists/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_setlists_search(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test searching setlists by name."""
        await client.post("/api/v1/setlists/", json=sample_setlist_data)
        await client.post("/api/v1/setlists/", json={"name": "Wednesday Prayer"})

        response = await client.get("/api/v1/setlists/?search=sunday")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Sunday Service"

    @pytest.mark.asyncio
    async def test_list_setlists_filter_by_event_type(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test filtering setlists by event type."""
        await client.post("/api/v1/setlists/", json=sample_setlist_data)
        await client.post(
            "/api/v1/setlists/",
            json={"name": "Youth Night", "event_type": "Youth"},
        )

        response = await client.get("/api/v1/setlists/?event_type=Sunday")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["event_type"] == "Sunday"

    @pytest.mark.asyncio
    async def test_list_setlists_pagination(self, client: AsyncClient) -> None:
        """Test pagination with skip and limit."""
        for i in range(5):
            await client.post("/api/v1/setlists/", json={"name": f"Setlist {i}"})

        # Get first 2
        response = await client.get("/api/v1/setlists/?limit=2")
        assert len(response.json()) == 2

        # Get next 2
        response = await client.get("/api/v1/setlists/?skip=2&limit=2")
        assert len(response.json()) == 2

        # Get last 1
        response = await client.get("/api/v1/setlists/?skip=4&limit=2")
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_list_setlists_includes_song_count(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test that list response includes song_count."""
        song_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = song_response.json()["id"]

        setlist_data = {
            **sample_setlist_data,
            "songs": [{"song_id": song_id, "position": 0}],
        }
        await client.post("/api/v1/setlists/", json=setlist_data)

        response = await client.get("/api/v1/setlists/")

        assert response.status_code == 200
        data = response.json()
        assert data[0]["song_count"] == 1


class TestGetSetlist:
    """Tests for GET /api/v1/setlists/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_setlist_success(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test getting a setlist by ID."""
        create_response = await client.post("/api/v1/setlists/", json=sample_setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/setlists/{setlist_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == setlist_id
        assert data["name"] == sample_setlist_data["name"]
        assert "songs" in data

    @pytest.mark.asyncio
    async def test_get_setlist_with_songs(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test getting a setlist includes full song data."""
        song_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = song_response.json()["id"]

        setlist_data = {
            **sample_setlist_data,
            "songs": [{"song_id": song_id, "position": 0}],
        }
        create_response = await client.post("/api/v1/setlists/", json=setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/setlists/{setlist_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["songs"]) == 1
        assert data["songs"][0]["song"]["name"] == sample_song_data["name"]
        assert data["songs"][0]["song"]["lyrics"] == sample_song_data["lyrics"]

    @pytest.mark.asyncio
    async def test_get_setlist_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent setlist returns 404."""
        fake_id = str(uuid4())

        response = await client.get(f"/api/v1/setlists/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_setlist_invalid_id(self, client: AsyncClient) -> None:
        """Test getting a setlist with invalid UUID format."""
        response = await client.get("/api/v1/setlists/not-a-uuid")

        assert response.status_code == 422


class TestUpdateSetlist:
    """Tests for PUT /api/v1/setlists/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_setlist_success(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test updating a setlist."""
        create_response = await client.post("/api/v1/setlists/", json=sample_setlist_data)
        setlist_id = create_response.json()["id"]

        updated_data = sample_setlist_data.copy()
        updated_data["name"] = "Updated Sunday Service"
        updated_data["description"] = "Updated description"

        response = await client.put(f"/api/v1/setlists/{setlist_id}", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Sunday Service"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_setlist_replace_songs(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test updating a setlist replaces songs."""
        # Create songs
        song1_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song1_id = song1_response.json()["id"]

        song2_response = await client.post("/api/v1/songs/", json={"name": "Second Song"})
        song2_id = song2_response.json()["id"]

        # Create setlist with first song
        setlist_data = {
            **sample_setlist_data,
            "songs": [{"song_id": song1_id, "position": 0}],
        }
        create_response = await client.post("/api/v1/setlists/", json=setlist_data)
        setlist_id = create_response.json()["id"]

        # Update with second song only
        updated_data = {
            **sample_setlist_data,
            "songs": [{"song_id": song2_id, "position": 0}],
        }
        response = await client.put(f"/api/v1/setlists/{setlist_id}", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["songs"]) == 1
        # Verify song2 is in the list (song1 was replaced)
        song_ids = [s["song"]["id"] for s in data["songs"]]
        assert song2_id in song_ids
        assert song1_id not in song_ids

    @pytest.mark.asyncio
    async def test_update_setlist_reorder_songs(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test reordering songs in a setlist."""
        # Create songs
        song1_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song1_id = song1_response.json()["id"]

        song2_response = await client.post("/api/v1/songs/", json={"name": "Second Song"})
        song2_id = song2_response.json()["id"]

        # Create setlist with both songs
        setlist_data = {
            **sample_setlist_data,
            "songs": [
                {"song_id": song1_id, "position": 0},
                {"song_id": song2_id, "position": 1},
            ],
        }
        create_response = await client.post("/api/v1/setlists/", json=setlist_data)
        setlist_id = create_response.json()["id"]

        # Reorder songs
        updated_data = {
            **sample_setlist_data,
            "songs": [
                {"song_id": song2_id, "position": 0},
                {"song_id": song1_id, "position": 1},
            ],
        }
        response = await client.put(f"/api/v1/setlists/{setlist_id}", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["songs"]) == 2

        # Create a map of song_id -> position from response
        song_positions = {s["song"]["id"]: s["position"] for s in data["songs"]}
        assert song_positions[song2_id] == 0
        assert song_positions[song1_id] == 1

    @pytest.mark.asyncio
    async def test_update_setlist_not_found(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test updating a non-existent setlist returns 404."""
        fake_id = str(uuid4())

        response = await client.put(f"/api/v1/setlists/{fake_id}", json=sample_setlist_data)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_setlist_invalid_data(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test updating with invalid data fails."""
        create_response = await client.post("/api/v1/setlists/", json=sample_setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/setlists/{setlist_id}",
            json={"name": "Test", "event_type": "InvalidType"},
        )

        assert response.status_code == 422


class TestDeleteSetlist:
    """Tests for DELETE /api/v1/setlists/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_setlist_success(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test deleting a setlist (requires admin/leader auth)."""
        headers = await get_admin_headers(client)
        create_response = await client.post("/api/v1/setlists/", json=sample_setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/setlists/{setlist_id}", headers=headers)

        assert response.status_code == 204

        # Verify setlist is deleted
        get_response = await client.get(f"/api/v1/setlists/{setlist_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_setlist_cascades_songs(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test deleting a setlist removes setlist-song associations but not songs."""
        headers = await get_admin_headers(client)
        # Create a song
        song_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = song_response.json()["id"]

        # Create setlist with song
        setlist_data = {
            **sample_setlist_data,
            "songs": [{"song_id": song_id, "position": 0}],
        }
        create_response = await client.post("/api/v1/setlists/", json=setlist_data)
        setlist_id = create_response.json()["id"]

        # Delete setlist
        await client.delete(f"/api/v1/setlists/{setlist_id}", headers=headers)

        # Song should still exist
        song_response = await client.get(f"/api/v1/songs/{song_id}")
        assert song_response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_setlist_not_found(self, client: AsyncClient) -> None:
        """Test deleting a non-existent setlist returns 404."""
        headers = await get_admin_headers(client)
        fake_id = str(uuid4())

        response = await client.delete(f"/api/v1/setlists/{fake_id}", headers=headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_setlist_invalid_id(self, client: AsyncClient) -> None:
        """Test deleting with invalid UUID format."""
        headers = await get_admin_headers(client)
        response = await client.delete("/api/v1/setlists/not-a-uuid", headers=headers)

        assert response.status_code == 422


class TestExportSetlist:
    """Tests for export endpoints."""

    @pytest.mark.asyncio
    async def test_export_freeshow_success(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test exporting a setlist to FreeShow format."""
        headers = await get_admin_headers(client)
        # Create song with lyrics
        song_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = song_response.json()["id"]

        # Create setlist with song
        setlist_data = {
            **sample_setlist_data,
            "songs": [{"song_id": song_id, "position": 0}],
        }
        create_response = await client.post("/api/v1/setlists/", json=setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/setlists/{setlist_id}/export/freeshow", headers=headers)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "attachment" in response.headers["content-disposition"]
        assert ".project" in response.headers["content-disposition"]

        # Verify it's valid JSON
        data = response.json()
        assert "project" in data
        assert "shows" in data

    @pytest.mark.asyncio
    async def test_export_freeshow_empty_setlist(
        self, client: AsyncClient, sample_setlist_data: dict[str, Any]
    ) -> None:
        """Test exporting an empty setlist returns 400 error."""
        headers = await get_admin_headers(client)
        create_response = await client.post("/api/v1/setlists/", json=sample_setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/setlists/{setlist_id}/export/freeshow", headers=headers)

        assert response.status_code == 400
        assert "empty setlist" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_export_freeshow_not_found(self, client: AsyncClient) -> None:
        """Test exporting a non-existent setlist returns 404."""
        headers = await get_admin_headers(client)
        fake_id = str(uuid4())

        response = await client.get(f"/api/v1/setlists/{fake_id}/export/freeshow", headers=headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_quelea_success(
        self,
        client: AsyncClient,
        sample_setlist_data: dict[str, Any],
        sample_song_data: dict[str, Any],
    ) -> None:
        """Test exporting a setlist to Quelea format."""
        headers = await get_admin_headers(client)
        # Create song with lyrics
        song_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = song_response.json()["id"]

        # Create setlist with song
        setlist_data = {
            **sample_setlist_data,
            "songs": [{"song_id": song_id, "position": 0}],
        }
        create_response = await client.post("/api/v1/setlists/", json=setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/setlists/{setlist_id}/export/quelea", headers=headers)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]
        assert ".qsch" in response.headers["content-disposition"]

        # Verify it's a valid ZIP
        assert response.content[:4] == b"PK\x03\x04"

    @pytest.mark.asyncio
    async def test_export_quelea_not_found(self, client: AsyncClient) -> None:
        """Test exporting a non-existent setlist returns 404."""
        headers = await get_admin_headers(client)
        fake_id = str(uuid4())

        response = await client.get(f"/api/v1/setlists/{fake_id}/export/quelea", headers=headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_filename_sanitization(
        self, client: AsyncClient, sample_song_data: dict[str, Any]
    ) -> None:
        """Test that export filename is sanitized."""
        headers = await get_admin_headers(client)
        # Create setlist with special characters in name
        song_response = await client.post("/api/v1/songs/", json=sample_song_data)
        song_id = song_response.json()["id"]

        setlist_data = {
            "name": "Sunday <Service> 01/12/2025",
            "songs": [{"song_id": song_id, "position": 0}],
        }
        create_response = await client.post("/api/v1/setlists/", json=setlist_data)
        setlist_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/setlists/{setlist_id}/export/freeshow", headers=headers)

        # Check filename doesn't contain special characters
        disposition = response.headers["content-disposition"]
        assert "<" not in disposition
        assert ">" not in disposition
        assert "/" not in disposition.split("filename=")[1]
