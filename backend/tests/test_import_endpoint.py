"""Tests for song import API endpoints."""

from pathlib import Path
from io import BytesIO

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.song import Song


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "import_samples"


@pytest.fixture
def sample_chordpro_content() -> bytes:
    """Sample ChordPro content for testing."""
    return b"""{title: Test Import Song}
{artist: Test Artist}
{key: G}

[G]This is a [D]test song
[Em]For testing [C]import
"""


class TestPreviewEndpoint:
    """Tests for POST /api/v1/songs/import/preview."""

    @pytest.mark.asyncio
    async def test_preview_single_file(
        self, client: AsyncClient, sample_chordpro_content: bytes
    ):
        """Should preview a single file successfully."""
        files = [("files", ("test.cho", sample_chordpro_content, "text/plain"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 1
        assert data["successful"] == 1
        assert data["failed"] == 0
        assert len(data["songs"]) == 1

        song = data["songs"][0]
        assert song["file_name"] == "test.cho"
        assert song["detected_format"] == "chordpro"
        assert song["success"] is True
        assert song["song_data"]["name"] == "Test Import Song"
        assert song["song_data"]["artist"] == "Test Artist"

    @pytest.mark.asyncio
    async def test_preview_multiple_files(
        self, client: AsyncClient, sample_chordpro_content: bytes
    ):
        """Should preview multiple files."""
        files = [
            ("files", ("song1.cho", sample_chordpro_content, "text/plain")),
            ("files", ("song2.cho", sample_chordpro_content, "text/plain")),
            ("files", ("song3.cho", sample_chordpro_content, "text/plain")),
        ]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 3
        assert data["successful"] == 3

    @pytest.mark.asyncio
    async def test_preview_with_failures(
        self,
        client: AsyncClient,
        sample_chordpro_content: bytes,
    ):
        """Should handle mixed success/failure with oversized file."""
        # Use oversized file to trigger actual failure
        # (binary content falls back to plaintext parser which succeeds)
        large_content = b"x" * (1024 * 1024 + 1)  # Over 1MB
        files = [
            ("files", ("good.cho", sample_chordpro_content, "text/plain")),
            ("files", ("large.txt", large_content, "text/plain")),
        ]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 2
        assert data["successful"] == 1
        assert data["failed"] == 1

    @pytest.mark.asyncio
    async def test_preview_no_files(self, client: AsyncClient):
        """Should reject request with no files."""
        response = await client.post("/api/v1/songs/import/preview", files=[])

        # FastAPI returns 422 for validation errors (empty required list)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_preview_file_too_large(self, client: AsyncClient):
        """Should reject files larger than 1MB."""
        large_content = b"x" * (1024 * 1024 + 1)  # Just over 1MB
        files = [("files", ("large.txt", large_content, "text/plain"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["failed"] == 1
        assert "exceeds maximum size" in data["songs"][0]["error"]

    @pytest.mark.asyncio
    async def test_preview_real_sample_files(self, client: AsyncClient):
        """Should preview real sample files from fixtures."""
        files_to_test = [
            ("sample.cho", "chordpro"),
            ("sample_openlyrics.xml", "openlyrics"),
            ("sample_opensong.xml", "opensong"),
            ("sample.txt", "plaintext"),
        ]

        for filename, expected_format in files_to_test:
            file_path = FIXTURES_DIR / filename
            if not file_path.exists():
                pytest.skip(f"Sample file {filename} not found")

            content = file_path.read_bytes()
            files = [("files", (filename, content, "text/plain"))]

            response = await client.post("/api/v1/songs/import/preview", files=files)

            assert response.status_code == 200, f"Failed for {filename}"
            data = response.json()
            assert data["successful"] == 1, f"Failed to parse {filename}"
            assert (
                data["songs"][0]["detected_format"] == expected_format
            ), f"Wrong format for {filename}"


class TestConfirmEndpoint:
    """Tests for POST /api/v1/songs/import/confirm."""

    @pytest.mark.asyncio
    async def test_confirm_saves_songs(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Should save songs to database."""
        request_data = {
            "songs": [
                {
                    "name": "Imported Song 1",
                    "artist": "Test Artist",
                    "original_key": "G",
                },
                {
                    "name": "Imported Song 2",
                    "artist": "Another Artist",
                    "original_key": "D",
                },
            ]
        }

        response = await client.post("/api/v1/songs/import/confirm", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["saved_count"] == 2
        assert len(data["songs"]) == 2

        # Verify songs have IDs
        assert data["songs"][0]["id"] is not None
        assert data["songs"][1]["id"] is not None

        # Verify names
        names = {s["name"] for s in data["songs"]}
        assert "Imported Song 1" in names
        assert "Imported Song 2" in names

    @pytest.mark.asyncio
    async def test_confirm_no_songs(self, client: AsyncClient):
        """Should reject request with no songs."""
        response = await client.post("/api/v1/songs/import/confirm", json={"songs": []})

        assert response.status_code == 400
        assert "No songs" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_confirm_validates_song_data(self, client: AsyncClient):
        """Should validate song data (name required)."""
        request_data = {
            "songs": [
                {"name": "", "artist": "Test"}  # Empty name should fail
            ]
        }

        response = await client.post("/api/v1/songs/import/confirm", json=request_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_full_import_flow(
        self, client: AsyncClient, sample_chordpro_content: bytes
    ):
        """Should complete full preview -> confirm flow."""
        # Step 1: Preview
        files = [("files", ("test.cho", sample_chordpro_content, "text/plain"))]
        preview_response = await client.post(
            "/api/v1/songs/import/preview", files=files
        )

        assert preview_response.status_code == 200
        preview_data = preview_response.json()
        assert preview_data["successful"] == 1

        # Get the song data from preview
        song_data = preview_data["songs"][0]["song_data"]

        # Step 2: Confirm
        confirm_response = await client.post(
            "/api/v1/songs/import/confirm", json={"songs": [song_data]}
        )

        assert confirm_response.status_code == 200
        confirm_data = confirm_response.json()
        assert confirm_data["saved_count"] == 1
        assert confirm_data["songs"][0]["name"] == "Test Import Song"

        # Step 3: Verify song exists in database
        song_id = confirm_data["songs"][0]["id"]
        get_response = await client.get(f"/api/v1/songs/{song_id}")

        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Test Import Song"
