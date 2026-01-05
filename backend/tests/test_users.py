"""Tests for user management endpoints."""

import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, email: str = "admin@test.com") -> dict:
    """Helper to register/login and get auth headers."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": "Test User",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestListUsers:
    """Tests for listing users."""

    @pytest.mark.asyncio
    async def test_list_users_as_admin(self, client: AsyncClient) -> None:
        """Admin can list all users."""
        headers = await get_auth_headers(client)  # First user is admin

        # Create another user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "member@test.com",
                "password": "testpassword123",
                "name": "Member User",
            },
        )

        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2

    @pytest.mark.asyncio
    async def test_list_users_as_member_forbidden(self, client: AsyncClient) -> None:
        """Member cannot list users."""
        # Create admin first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "testpassword123",
                "name": "Admin User",
            },
        )

        # Create and login as member
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "member@test.com",
                "password": "testpassword123",
                "name": "Member User",
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "member@test.com", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_users_unauthenticated(self, client: AsyncClient) -> None:
        """Unauthenticated request fails."""
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401


class TestUpdateUserRole:
    """Tests for updating user roles."""

    @pytest.mark.asyncio
    async def test_admin_can_change_user_role(self, client: AsyncClient) -> None:
        """Admin can change another user's role."""
        headers = await get_auth_headers(client)

        # Create member
        member_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "member@test.com",
                "password": "testpassword123",
                "name": "Member User",
            },
        )
        member_id = member_response.json()["id"]

        # Change role to leader
        response = await client.put(
            f"/api/v1/users/{member_id}/role",
            headers=headers,
            json={"role": "leader"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "leader"

    @pytest.mark.asyncio
    async def test_admin_cannot_change_own_role(self, client: AsyncClient) -> None:
        """Admin cannot change their own role."""
        # Register admin
        admin_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "testpassword123",
                "name": "Admin User",
            },
        )
        admin_id = admin_response.json()["id"]

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to change own role
        response = await client.put(
            f"/api/v1/users/{admin_id}/role",
            headers=headers,
            json={"role": "member"},
        )
        assert response.status_code == 400
        assert "Cannot change your own role" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_leader_cannot_change_roles(self, client: AsyncClient) -> None:
        """Leader cannot change user roles (admin only)."""
        # Create admin
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "testpassword123",
                "name": "Admin User",
            },
        )
        admin_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "testpassword123"},
        )
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create member
        member_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "member@test.com",
                "password": "testpassword123",
                "name": "Member User",
            },
        )
        member_id = member_response.json()["id"]

        # Promote to leader
        await client.put(
            f"/api/v1/users/{member_id}/role",
            headers=admin_headers,
            json={"role": "leader"},
        )

        # Login as leader
        leader_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "member@test.com", "password": "testpassword123"},
        )
        leader_token = leader_login.json()["access_token"]
        leader_headers = {"Authorization": f"Bearer {leader_token}"}

        # Create another member
        another_member_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "another@test.com",
                "password": "testpassword123",
                "name": "Another User",
            },
        )
        another_id = another_member_response.json()["id"]

        # Try to change role as leader
        response = await client.put(
            f"/api/v1/users/{another_id}/role",
            headers=leader_headers,
            json={"role": "leader"},
        )
        assert response.status_code == 403


class TestDeactivateUser:
    """Tests for deactivating users."""

    @pytest.mark.asyncio
    async def test_admin_can_deactivate_user(self, client: AsyncClient) -> None:
        """Admin can deactivate another user."""
        headers = await get_auth_headers(client)

        # Create member
        member_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "member@test.com",
                "password": "testpassword123",
                "name": "Member User",
            },
        )
        member_id = member_response.json()["id"]

        # Deactivate
        response = await client.delete(
            f"/api/v1/users/{member_id}",
            headers=headers,
        )
        assert response.status_code == 204

        # Verify user is deactivated
        get_response = await client.get(
            f"/api/v1/users/{member_id}",
            headers=headers,
        )
        assert get_response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_admin_cannot_deactivate_self(self, client: AsyncClient) -> None:
        """Admin cannot deactivate themselves."""
        admin_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "testpassword123",
                "name": "Admin User",
            },
        )
        admin_id = admin_response.json()["id"]

        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.delete(
            f"/api/v1/users/{admin_id}",
            headers=headers,
        )
        assert response.status_code == 400
        assert "Cannot deactivate yourself" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_deactivated_user_cannot_login(self, client: AsyncClient) -> None:
        """Deactivated user cannot login."""
        headers = await get_auth_headers(client)

        # Create member
        member_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "member@test.com",
                "password": "testpassword123",
                "name": "Member User",
            },
        )
        member_id = member_response.json()["id"]

        # Deactivate
        await client.delete(f"/api/v1/users/{member_id}", headers=headers)

        # Try to login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "member@test.com", "password": "testpassword123"},
        )
        assert login_response.status_code == 403
        assert "Inactive user" in login_response.json()["detail"]
