"""Tests for song import API endpoints."""

import zipfile
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
            ("sample.txt", "ultimateguitar"),
            ("sample_plaintext.txt", "plaintext"),
            ("sample_ug.txt", "ultimateguitar"),
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


class TestUrlPreviewEndpoint:
    """Tests for POST /api/v1/songs/import/preview-url."""

    @pytest.mark.asyncio
    async def test_preview_url_invalid_url(self, client: AsyncClient):
        """Should reject invalid URL."""
        response = await client.post(
            "/api/v1/songs/import/preview-url",
            json={"url": "not-a-valid-url"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_preview_url_unreachable(self, client: AsyncClient):
        """Should handle unreachable URL gracefully."""
        response = await client.post(
            "/api/v1/songs/import/preview-url",
            json={"url": "https://this-domain-does-not-exist-12345.com/song.cho"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["failed"] == 1
        assert data["songs"][0]["success"] is False
        assert "Failed to fetch URL" in data["songs"][0]["error"]

    @pytest.mark.asyncio
    async def test_preview_url_missing_url(self, client: AsyncClient):
        """Should reject request without URL."""
        response = await client.post(
            "/api/v1/songs/import/preview-url",
            json={},
        )

        assert response.status_code == 422


class TestZipImport:
    """Tests for ZIP archive import."""

    @pytest.fixture
    def create_zip(self) -> callable:
        """Factory to create ZIP archives with song files."""

        def _create_zip(files: list[tuple[str, bytes]]) -> bytes:
            buffer = BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for filename, content in files:
                    zf.writestr(filename, content)
            return buffer.getvalue()

        return _create_zip

    @pytest.mark.asyncio
    async def test_preview_zip_single_song(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should extract and preview a single song from ZIP."""
        zip_content = create_zip([("song.cho", sample_chordpro_content)])
        files = [("files", ("songs.zip", zip_content, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 1
        assert data["successful"] == 1
        assert data["songs"][0]["success"] is True
        assert "songs.zip/song.cho" in data["songs"][0]["file_name"]

    @pytest.mark.asyncio
    async def test_preview_zip_multiple_songs(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should extract and preview multiple songs from ZIP."""
        song1 = b"""{title: Song One}
{artist: Artist A}

[G]First song lyrics"""

        song2 = b"""{title: Song Two}
{artist: Artist B}

[C]Second song lyrics"""

        zip_content = create_zip([
            ("song1.cho", song1),
            ("song2.cho", song2),
            ("song3.txt", b"Just plain text lyrics"),
        ])
        files = [("files", ("songs.zip", zip_content, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 3
        assert data["successful"] == 3

    @pytest.mark.asyncio
    async def test_preview_zip_filters_non_song_files(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should only extract song files from ZIP, ignoring others."""
        zip_content = create_zip([
            ("song.cho", sample_chordpro_content),
            ("readme.md", b"# README"),
            ("image.png", b"PNG data"),
            ("config.json", b"{}"),
        ])
        files = [("files", ("songs.zip", zip_content, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        # Only .cho file should be extracted
        assert data["total_files"] == 1
        assert data["successful"] == 1

    @pytest.mark.asyncio
    async def test_preview_zip_ignores_macosx_folder(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should ignore __MACOSX folder in ZIP."""
        zip_content = create_zip([
            ("song.cho", sample_chordpro_content),
            ("__MACOSX/._song.cho", b"metadata"),
        ])
        files = [("files", ("songs.zip", zip_content, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 1
        assert data["successful"] == 1

    @pytest.mark.asyncio
    async def test_preview_zip_ignores_hidden_files(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should ignore hidden files (starting with .) in ZIP."""
        zip_content = create_zip([
            ("song.cho", sample_chordpro_content),
            (".hidden.cho", sample_chordpro_content),
            ("folder/.hidden.txt", b"hidden"),
        ])
        files = [("files", ("songs.zip", zip_content, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        # Only non-hidden song file should be extracted
        assert data["total_files"] == 1
        assert data["successful"] == 1

    @pytest.mark.asyncio
    async def test_preview_zip_nested_folders(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should extract song files from nested folders."""
        zip_content = create_zip([
            ("songs/worship/song1.cho", sample_chordpro_content),
            ("songs/hymns/song2.cho", sample_chordpro_content),
        ])
        files = [("files", ("songs.zip", zip_content, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 2
        assert data["successful"] == 2

    @pytest.mark.asyncio
    async def test_preview_zip_with_invalid_zip(self, client: AsyncClient):
        """Should handle invalid ZIP gracefully."""
        # Starts with ZIP magic bytes but is corrupted
        fake_zip = b"PK\x03\x04corrupted content that is not a valid zip"
        files = [("files", ("songs.zip", fake_zip, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["failed"] >= 1
        # Should have an error message about invalid ZIP
        assert any("Invalid ZIP" in (s.get("error") or "") or "Failed to read" in (s.get("error") or "")
                   for s in data["songs"])

    @pytest.mark.asyncio
    async def test_preview_zip_mixed_with_regular_files(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should handle ZIP and regular files in same request."""
        zip_content = create_zip([("zipped_song.cho", sample_chordpro_content)])

        files = [
            ("files", ("regular.cho", sample_chordpro_content, "text/plain")),
            ("files", ("archive.zip", zip_content, "application/zip")),
        ]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 2
        assert data["successful"] == 2

    @pytest.mark.asyncio
    async def test_preview_zip_all_supported_extensions(
        self, client: AsyncClient, sample_chordpro_content: bytes, create_zip: callable
    ):
        """Should extract all supported song file extensions."""
        zip_content = create_zip([
            ("song.cho", sample_chordpro_content),
            ("song.crd", sample_chordpro_content),
            ("song.chopro", sample_chordpro_content),
            ("song.txt", b"Plain text song"),
            ("song.xml", b"<song><lyrics>test</lyrics></song>"),
            ("song.onsong", sample_chordpro_content),
        ])
        files = [("files", ("songs.zip", zip_content, "application/zip"))]

        response = await client.post("/api/v1/songs/import/preview", files=files)

        assert response.status_code == 200
        data = response.json()
        # All 6 supported extensions should be extracted
        assert data["total_files"] == 6
