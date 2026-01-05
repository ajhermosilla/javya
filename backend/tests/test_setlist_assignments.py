"""Tests for setlist assignment endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


async def register_and_login(
    client: AsyncClient,
    email: str,
    name: str = "Test User",
) -> tuple[str, dict]:
    """Register a user and return (user_id, auth_headers)."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name,
        },
    )
    user_id = register_response.json()["id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return user_id, headers


async def create_setlist(client: AsyncClient, headers: dict) -> str:
    """Create a setlist and return its ID."""
    response = await client.post(
        "/api/v1/setlists/",
        headers=headers,
        json={
            "name": "Sunday Service",
            "service_date": "2026-01-12",
            "event_type": "Sunday",
        },
    )
    return response.json()["id"]


class TestCreateAssignment:
    """Tests for POST /api/v1/setlists/{id}/assignments endpoint."""

    @pytest.mark.asyncio
    async def test_create_assignment_as_admin(self, client: AsyncClient) -> None:
        """Admin can create an assignment."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={
                "user_id": member_id,
                "service_role": "vocalist",
                "notes": "Lead vocals",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == member_id
        assert data["service_role"] == "vocalist"
        assert data["notes"] == "Lead vocals"
        assert data["confirmed"] is False
        assert data["user_name"] == "Member"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_assignment_as_leader(self, client: AsyncClient) -> None:
        """Leader can create an assignment."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        leader_id, _ = await register_and_login(client, "leader@test.com", "Leader")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        # Promote to leader
        await client.put(
            f"/api/v1/users/{leader_id}/role",
            headers=admin_headers,
            json={"role": "leader"},
        )

        # Login again as leader
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "leader@test.com", "password": "testpassword123"},
        )
        leader_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        setlist_id = await create_setlist(client, admin_headers)

        response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=leader_headers,
            json={
                "user_id": member_id,
                "service_role": "guitarist",
            },
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_assignment_as_member_forbidden(self, client: AsyncClient) -> None:
        """Member cannot create an assignment."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=member_headers,
            json={
                "user_id": member_id,
                "service_role": "vocalist",
            },
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_assignment_duplicate_fails(self, client: AsyncClient) -> None:
        """Cannot create duplicate assignment (same user, same role, same setlist)."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        # First assignment
        await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={
                "user_id": member_id,
                "service_role": "vocalist",
            },
        )

        # Duplicate
        response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={
                "user_id": member_id,
                "service_role": "vocalist",
            },
        )

        assert response.status_code == 409
        assert "already assigned" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_assignment_same_user_different_roles(self, client: AsyncClient) -> None:
        """Same user can have multiple roles in a setlist."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        # First role
        response1 = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assert response1.status_code == 201

        # Second role
        response2 = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "guitarist"},
        )
        assert response2.status_code == 201

    @pytest.mark.asyncio
    async def test_create_assignment_invalid_user(self, client: AsyncClient) -> None:
        """Cannot assign a non-existent user."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        setlist_id = await create_setlist(client, admin_headers)

        response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={
                "user_id": str(uuid4()),
                "service_role": "vocalist",
            },
        )

        assert response.status_code == 404
        assert "User" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_assignment_invalid_setlist(self, client: AsyncClient) -> None:
        """Cannot assign to a non-existent setlist."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        response = await client.post(
            f"/api/v1/setlists/{uuid4()}/assignments",
            headers=admin_headers,
            json={
                "user_id": member_id,
                "service_role": "vocalist",
            },
        )

        assert response.status_code == 404
        assert "Setlist" in response.json()["detail"]


class TestListAssignments:
    """Tests for GET /api/v1/setlists/{id}/assignments endpoint."""

    @pytest.mark.asyncio
    async def test_list_assignments_empty(self, client: AsyncClient) -> None:
        """List assignments returns empty list for new setlist."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        setlist_id = await create_setlist(client, admin_headers)

        response = await client.get(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_assignments_with_data(self, client: AsyncClient) -> None:
        """List assignments returns all assignments."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        # Create assignments
        await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": admin_id, "service_role": "worship_leader"},
        )

        response = await client.get(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_assignments_as_member(self, client: AsyncClient) -> None:
        """Members can view assignments."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        response = await client.get(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=member_headers,
        )

        assert response.status_code == 200


class TestUpdateAssignment:
    """Tests for PUT /api/v1/setlists/{id}/assignments/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_assignment_role(self, client: AsyncClient) -> None:
        """Admin can update assignment role."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}",
            headers=admin_headers,
            json={"service_role": "guitarist"},
        )

        assert response.status_code == 200
        assert response.json()["service_role"] == "guitarist"

    @pytest.mark.asyncio
    async def test_update_assignment_notes(self, client: AsyncClient) -> None:
        """Admin can update assignment notes."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}",
            headers=admin_headers,
            json={"notes": "Lead vocals on song 2"},
        )

        assert response.status_code == 200
        assert response.json()["notes"] == "Lead vocals on song 2"

    @pytest.mark.asyncio
    async def test_update_assignment_as_member_forbidden(self, client: AsyncClient) -> None:
        """Member cannot update assignments."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}",
            headers=member_headers,
            json={"service_role": "guitarist"},
        )

        assert response.status_code == 403


class TestDeleteAssignment:
    """Tests for DELETE /api/v1/setlists/{id}/assignments/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_assignment_success(self, client: AsyncClient) -> None:
        """Admin can delete an assignment."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, _ = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}",
            headers=admin_headers,
        )

        assert response.status_code == 204

        # Verify it's gone
        list_response = await client.get(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
        )
        assert len(list_response.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_assignment_as_member_forbidden(self, client: AsyncClient) -> None:
        """Member cannot delete assignments."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}",
            headers=member_headers,
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_assignment_not_found(self, client: AsyncClient) -> None:
        """Delete non-existent assignment returns 404."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        setlist_id = await create_setlist(client, admin_headers)

        response = await client.delete(
            f"/api/v1/setlists/{setlist_id}/assignments/{uuid4()}",
            headers=admin_headers,
        )

        assert response.status_code == 404


class TestConfirmAssignment:
    """Tests for PATCH /api/v1/setlists/{id}/assignments/{id}/confirm endpoint."""

    @pytest.mark.asyncio
    async def test_confirm_own_assignment(self, client: AsyncClient) -> None:
        """User can confirm their own assignment."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}/confirm",
            headers=member_headers,
            json={"confirmed": True},
        )

        assert response.status_code == 200
        assert response.json()["confirmed"] is True

    @pytest.mark.asyncio
    async def test_unconfirm_own_assignment(self, client: AsyncClient) -> None:
        """User can unconfirm their own assignment."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        setlist_id = await create_setlist(client, admin_headers)

        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        # Confirm
        await client.patch(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}/confirm",
            headers=member_headers,
            json={"confirmed": True},
        )

        # Unconfirm
        response = await client.patch(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}/confirm",
            headers=member_headers,
            json={"confirmed": False},
        )

        assert response.status_code == 200
        assert response.json()["confirmed"] is False

    @pytest.mark.asyncio
    async def test_cannot_confirm_others_assignment(self, client: AsyncClient) -> None:
        """User cannot confirm another user's assignment."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member1_id, member1_headers = await register_and_login(client, "member1@test.com", "Member 1")
        member2_id, member2_headers = await register_and_login(client, "member2@test.com", "Member 2")

        setlist_id = await create_setlist(client, admin_headers)

        # Assign member1
        create_response = await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member1_id, "service_role": "vocalist"},
        )
        assignment_id = create_response.json()["id"]

        # Member2 tries to confirm member1's assignment
        response = await client.patch(
            f"/api/v1/setlists/{setlist_id}/assignments/{assignment_id}/confirm",
            headers=member2_headers,
            json={"confirmed": True},
        )

        assert response.status_code == 403
        assert "your own" in response.json()["detail"]


class TestSchedulingEndpoints:
    """Tests for scheduling endpoints."""

    @pytest.mark.asyncio
    async def test_get_calendar(self, client: AsyncClient) -> None:
        """Get calendar returns setlists in date range."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")

        # Create setlists
        await client.post(
            "/api/v1/setlists/",
            headers=admin_headers,
            json={"name": "Jan Service", "service_date": "2026-01-15", "event_type": "Sunday"},
        )
        await client.post(
            "/api/v1/setlists/",
            headers=admin_headers,
            json={"name": "Feb Service", "service_date": "2026-02-15", "event_type": "Sunday"},
        )

        response = await client.get(
            "/api/v1/scheduling/calendar",
            headers=admin_headers,
            params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Jan Service"

    @pytest.mark.asyncio
    async def test_get_my_assignments(self, client: AsyncClient) -> None:
        """Get my assignments returns only current user's assignments."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        setlist_response = await client.post(
            "/api/v1/setlists/",
            headers=admin_headers,
            json={"name": "Sunday Service", "service_date": "2026-01-15", "event_type": "Sunday"},
        )
        setlist_id = setlist_response.json()["id"]

        # Assign member
        await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": member_id, "service_role": "vocalist"},
        )
        # Assign admin
        await client.post(
            f"/api/v1/setlists/{setlist_id}/assignments",
            headers=admin_headers,
            json={"user_id": admin_id, "service_role": "worship_leader"},
        )

        # Member should only see their assignment
        response = await client.get(
            "/api/v1/scheduling/my-assignments",
            headers=member_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["service_role"] == "vocalist"

    @pytest.mark.asyncio
    async def test_check_team_availability(self, client: AsyncClient) -> None:
        """Check team availability returns all users with status."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        # Set member's availability
        await client.post(
            "/api/v1/availability/",
            headers=member_headers,
            json={"date": "2026-01-15", "status": "available"},
        )

        response = await client.get(
            "/api/v1/scheduling/availability",
            headers=admin_headers,
            params={"service_date": "2026-01-15"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # admin and member

        # Find member in results
        member_data = next(u for u in data if u["user_id"] == member_id)
        assert member_data["availability_status"] == "available"

    @pytest.mark.asyncio
    async def test_check_team_availability_member_forbidden(self, client: AsyncClient) -> None:
        """Member cannot check team availability."""
        admin_id, admin_headers = await register_and_login(client, "admin@test.com", "Admin")
        member_id, member_headers = await register_and_login(client, "member@test.com", "Member")

        response = await client.get(
            "/api/v1/scheduling/availability",
            headers=member_headers,
            params={"service_date": "2026-01-15"},
        )

        assert response.status_code == 403
