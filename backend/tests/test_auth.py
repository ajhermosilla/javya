"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestRegister:
    """Tests for user registration."""

    @pytest.mark.asyncio
    async def test_register_first_user_becomes_admin(self, client: AsyncClient) -> None:
        """First user to register should become admin."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "testpassword123",
                "name": "Admin User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["name"] == "Admin User"
        assert data["role"] == "admin"
        assert data["is_active"] is True
        assert "id" in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_second_user_becomes_member(self, client: AsyncClient) -> None:
        """Second user to register should become member."""
        # First user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "testpassword123",
                "name": "Admin User",
            },
        )

        # Second user
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "member@test.com",
                "password": "testpassword123",
                "name": "Regular Member",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "member"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        """Cannot register with duplicate email."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "testpassword123",
                "name": "Test User",
            },
        )

        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "differentpassword",
                "name": "Another User",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        """Cannot register with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "notanemail",
                "password": "testpassword123",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient) -> None:
        """Cannot register with password shorter than 8 characters."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "short",
                "name": "Test User",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient) -> None:
        """Login with correct credentials returns token."""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "testpassword123",
                "name": "Test User",
            },
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@test.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient) -> None:
        """Login with wrong password fails."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "testpassword123",
                "name": "Test User",
            },
        )

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@test.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        """Login with nonexistent email fails."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@test.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 401


class TestGetMe:
    """Tests for /me endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client: AsyncClient) -> None:
        """Authenticated user can get their info."""
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "testpassword123",
                "name": "Test User",
            },
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@test.com",
                "password": "testpassword123",
            },
        )
        token = login_response.json()["access_token"]

        # Get user info
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@test.com"
        assert data["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient) -> None:
        """Unauthenticated request fails."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient) -> None:
        """Invalid token fails."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert response.status_code == 401
