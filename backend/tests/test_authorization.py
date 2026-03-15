"""Tests that member users get 403 on admin/leader-only endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMemberForbidden:
    """Member role should be denied access to admin/leader operations."""

    async def _create_song(self, client: AsyncClient, auth_headers: dict) -> str:
        """Helper: create a song as admin and return its ID."""
        response = await client.post(
            "/api/v1/songs/",
            headers=auth_headers,
            json={"name": "Test Song"},
        )
        return response.json()["id"]

    async def _create_setlist(self, client: AsyncClient, auth_headers: dict) -> str:
        """Helper: create a setlist as admin and return its ID."""
        response = await client.post(
            "/api/v1/setlists/",
            headers=auth_headers,
            json={"name": "Test Setlist"},
        )
        return response.json()["id"]

    # Songs

    async def test_delete_song_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        song_id = await self._create_song(client, auth_headers)
        response = await client.delete(f"/api/v1/songs/{song_id}", headers=member_headers)
        assert response.status_code == 403

    # Setlists

    async def test_delete_setlist_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        setlist_id = await self._create_setlist(client, auth_headers)
        response = await client.delete(f"/api/v1/setlists/{setlist_id}", headers=member_headers)
        assert response.status_code == 403

    # Users

    async def test_list_users_as_member(
        self, client: AsyncClient, member_headers: dict
    ) -> None:
        response = await client.get("/api/v1/users/", headers=member_headers)
        assert response.status_code == 403

    async def test_get_user_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        me = await client.get("/api/v1/auth/me", headers=member_headers)
        user_id = me.json()["id"]
        response = await client.get(f"/api/v1/users/{user_id}", headers=member_headers)
        assert response.status_code == 403

    async def test_change_role_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        # Get member user ID
        me = await client.get("/api/v1/auth/me", headers=member_headers)
        user_id = me.json()["id"]
        response = await client.put(
            f"/api/v1/users/{user_id}/role",
            headers=member_headers,
            json={"role": "admin"},
        )
        assert response.status_code == 403

    async def test_deactivate_user_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        me = await client.get("/api/v1/auth/me", headers=member_headers)
        user_id = me.json()["id"]
        response = await client.delete(f"/api/v1/users/{user_id}", headers=member_headers)
        assert response.status_code == 403

    # Setlist Assignments

    async def test_create_assignment_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        setlist_id = await self._create_setlist(client, auth_headers)
        me = await client.get("/api/v1/auth/me", headers=member_headers)
        user_id = me.json()["id"]
        response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=member_headers,
            json={"user_id": user_id, "service_role": "vocalist"},
        )
        assert response.status_code == 403

    async def test_update_assignment_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        setlist_id = await self._create_setlist(client, auth_headers)
        me = await client.get("/api/v1/auth/me", headers=member_headers)
        user_id = me.json()["id"]
        # Create assignment as admin
        create_resp = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=auth_headers,
            json={"user_id": user_id, "service_role": "vocalist"},
        )
        assignment_id = create_resp.json()["id"]
        # Try to update as member
        response = await client.put(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}",
            headers=member_headers,
            json={"service_role": "guitarist"},
        )
        assert response.status_code == 403

    async def test_delete_assignment_as_member(
        self, client: AsyncClient, auth_headers: dict, member_headers: dict
    ) -> None:
        setlist_id = await self._create_setlist(client, auth_headers)
        me = await client.get("/api/v1/auth/me", headers=member_headers)
        user_id = me.json()["id"]
        create_resp = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=auth_headers,
            json={"user_id": user_id, "service_role": "vocalist"},
        )
        assignment_id = create_resp.json()["id"]
        response = await client.delete(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}",
            headers=member_headers,
        )
        assert response.status_code == 403

    # Availability

    async def test_team_availability_as_member(
        self, client: AsyncClient, member_headers: dict
    ) -> None:
        response = await client.get(
            "/api/v1/availability/team?start_date=2099-01-01&end_date=2099-01-31",
            headers=member_headers,
        )
        assert response.status_code == 403

    # Scheduling

    async def test_team_availability_scheduling_as_member(
        self, client: AsyncClient, member_headers: dict
    ) -> None:
        response = await client.get(
            "/api/v1/scheduling/availability?service_date=2099-01-15",
            headers=member_headers,
        )
        assert response.status_code == 403
