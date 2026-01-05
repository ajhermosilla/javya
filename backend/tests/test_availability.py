"""Tests for availability endpoints."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


async def register_and_login(client: AsyncClient, email: str, name: str = "Test User") -> str:
    """Helper to register a user and return their access token."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name,
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "testpassword123"},
    )
    return response.json()["access_token"]


class TestSetAvailability:
    """Tests for setting availability."""

    @pytest.mark.asyncio
    async def test_set_availability_creates_entry(self, client: AsyncClient) -> None:
        """Can create new availability entry."""
        token = await register_and_login(client, "test@test.com")

        response = await client.post(
            "/api/v1/availability/",
            json={
                "date": str(date.today()),
                "status": "available",
                "note": "Free all day",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "available"
        assert data["note"] == "Free all day"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_set_availability_updates_existing(self, client: AsyncClient) -> None:
        """Setting availability for same date updates existing entry."""
        token = await register_and_login(client, "test@test.com")
        today = str(date.today())

        # Create first entry
        await client.post(
            "/api/v1/availability/",
            json={"date": today, "status": "available"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Update to unavailable
        response = await client.post(
            "/api/v1/availability/",
            json={"date": today, "status": "unavailable", "note": "Changed plans"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "unavailable"
        assert data["note"] == "Changed plans"

    @pytest.mark.asyncio
    async def test_set_availability_maybe_status(self, client: AsyncClient) -> None:
        """Can set maybe status."""
        token = await register_and_login(client, "test@test.com")

        response = await client.post(
            "/api/v1/availability/",
            json={"date": str(date.today()), "status": "maybe"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["status"] == "maybe"

    @pytest.mark.asyncio
    async def test_set_availability_unauthenticated(self, client: AsyncClient) -> None:
        """Unauthenticated user cannot set availability."""
        response = await client.post(
            "/api/v1/availability/",
            json={"date": str(date.today()), "status": "available"},
        )
        assert response.status_code == 401


class TestBulkAvailability:
    """Tests for bulk availability operations."""

    @pytest.mark.asyncio
    async def test_bulk_set_availability(self, client: AsyncClient) -> None:
        """Can set availability for multiple dates at once."""
        token = await register_and_login(client, "test@test.com")
        today = date.today()

        response = await client.post(
            "/api/v1/availability/bulk",
            json={
                "entries": [
                    {"date": str(today), "status": "available"},
                    {"date": str(today + timedelta(days=1)), "status": "unavailable"},
                    {"date": str(today + timedelta(days=2)), "status": "maybe"},
                ]
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestGetMyAvailability:
    """Tests for getting own availability."""

    @pytest.mark.asyncio
    async def test_get_my_availability(self, client: AsyncClient) -> None:
        """Can get own availability for date range."""
        token = await register_and_login(client, "test@test.com")
        today = date.today()

        # Set some availability
        await client.post(
            "/api/v1/availability/",
            json={"date": str(today), "status": "available"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            "/api/v1/availability/",
            json={"date": str(today + timedelta(days=1)), "status": "unavailable"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Get availability
        response = await client.get(
            "/api/v1/availability/me",
            params={
                "start_date": str(today),
                "end_date": str(today + timedelta(days=7)),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_my_availability_empty_range(self, client: AsyncClient) -> None:
        """Getting availability for date range with no entries returns empty list."""
        token = await register_and_login(client, "test@test.com")
        today = date.today()

        response = await client.get(
            "/api/v1/availability/me",
            params={
                "start_date": str(today),
                "end_date": str(today + timedelta(days=7)),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == []


class TestTeamAvailability:
    """Tests for team availability view."""

    @pytest.mark.asyncio
    async def test_admin_can_view_team_availability(self, client: AsyncClient) -> None:
        """Admin can view team availability."""
        # First user is admin
        admin_token = await register_and_login(client, "admin@test.com", "Admin")
        member_token = await register_and_login(client, "member@test.com", "Member")

        today = date.today()

        # Set availability for both
        await client.post(
            "/api/v1/availability/",
            json={"date": str(today), "status": "available"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        await client.post(
            "/api/v1/availability/",
            json={"date": str(today), "status": "unavailable"},
            headers={"Authorization": f"Bearer {member_token}"},
        )

        # Admin gets team view
        response = await client.get(
            "/api/v1/availability/team",
            params={
                "start_date": str(today),
                "end_date": str(today + timedelta(days=7)),
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Check it includes user info
        assert all("user_name" in entry for entry in data)
        assert all("user_email" in entry for entry in data)

    @pytest.mark.asyncio
    async def test_member_cannot_view_team_availability(self, client: AsyncClient) -> None:
        """Regular member cannot view team availability."""
        await register_and_login(client, "admin@test.com")
        member_token = await register_and_login(client, "member@test.com")

        today = date.today()
        response = await client.get(
            "/api/v1/availability/team",
            params={
                "start_date": str(today),
                "end_date": str(today + timedelta(days=7)),
            },
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 403


class TestDeleteAvailability:
    """Tests for deleting availability."""

    @pytest.mark.asyncio
    async def test_delete_own_availability(self, client: AsyncClient) -> None:
        """Can delete own availability entry."""
        token = await register_and_login(client, "test@test.com")

        # Create entry
        create_response = await client.post(
            "/api/v1/availability/",
            json={"date": str(date.today()), "status": "available"},
            headers={"Authorization": f"Bearer {token}"},
        )
        entry_id = create_response.json()["id"]

        # Delete it
        response = await client.delete(
            f"/api/v1/availability/{entry_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_cannot_delete_others_availability(self, client: AsyncClient) -> None:
        """Cannot delete another user's availability (unless admin)."""
        await register_and_login(client, "admin@test.com")
        member_token = await register_and_login(client, "member@test.com")
        other_token = await register_and_login(client, "other@test.com")

        # Member creates availability
        create_response = await client.post(
            "/api/v1/availability/",
            json={"date": str(date.today()), "status": "available"},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        entry_id = create_response.json()["id"]

        # Other member tries to delete
        response = await client.delete(
            f"/api/v1/availability/{entry_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 403


class TestAvailabilityPatterns:
    """Tests for availability patterns."""

    @pytest.mark.asyncio
    async def test_create_pattern(self, client: AsyncClient) -> None:
        """Can create availability pattern."""
        token = await register_and_login(client, "test@test.com")

        response = await client.post(
            "/api/v1/availability/patterns",
            json={
                "pattern_type": "weekly",
                "day_of_week": 0,  # Monday
                "status": "available",
                "note": "Free on Mondays",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["pattern_type"] == "weekly"
        assert data["day_of_week"] == 0
        assert data["status"] == "available"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_my_patterns(self, client: AsyncClient) -> None:
        """Can get own patterns."""
        token = await register_and_login(client, "test@test.com")

        # Create patterns
        await client.post(
            "/api/v1/availability/patterns",
            json={"pattern_type": "weekly", "day_of_week": 0, "status": "available"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            "/api/v1/availability/patterns",
            json={"pattern_type": "weekly", "day_of_week": 6, "status": "unavailable"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            "/api/v1/availability/patterns",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_update_pattern(self, client: AsyncClient) -> None:
        """Can update pattern."""
        token = await register_and_login(client, "test@test.com")

        # Create pattern
        create_response = await client.post(
            "/api/v1/availability/patterns",
            json={"pattern_type": "weekly", "day_of_week": 0, "status": "available"},
            headers={"Authorization": f"Bearer {token}"},
        )
        pattern_id = create_response.json()["id"]

        # Update it
        response = await client.put(
            f"/api/v1/availability/patterns/{pattern_id}",
            json={"status": "unavailable", "is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_delete_pattern(self, client: AsyncClient) -> None:
        """Can delete pattern."""
        token = await register_and_login(client, "test@test.com")

        # Create pattern
        create_response = await client.post(
            "/api/v1/availability/patterns",
            json={"pattern_type": "weekly", "day_of_week": 0, "status": "available"},
            headers={"Authorization": f"Bearer {token}"},
        )
        pattern_id = create_response.json()["id"]

        # Delete it
        response = await client.delete(
            f"/api/v1/availability/patterns/{pattern_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_cannot_update_others_pattern(self, client: AsyncClient) -> None:
        """Cannot update another user's pattern."""
        await register_and_login(client, "admin@test.com")
        member_token = await register_and_login(client, "member@test.com")
        other_token = await register_and_login(client, "other@test.com")

        # Member creates pattern
        create_response = await client.post(
            "/api/v1/availability/patterns",
            json={"pattern_type": "weekly", "day_of_week": 0, "status": "available"},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        pattern_id = create_response.json()["id"]

        # Other member tries to update
        response = await client.put(
            f"/api/v1/availability/patterns/{pattern_id}",
            json={"status": "unavailable"},
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 403
