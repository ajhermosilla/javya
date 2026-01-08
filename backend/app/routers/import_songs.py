"""Router for song import endpoints."""

import zipfile
from io import BytesIO
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_db
from app.models.song import Song
from app.schemas.import_song import (
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
    ParsedSong,
    UrlImportRequest,
)
from app.schemas.duplicate import ExistingSongSummary, SongCheck
from app.schemas.song import SongResponse
from app.services.duplicate_detector import find_duplicates
from app.services.import_song import detect_and_parse

router = APIRouter()

# Limits
MAX_FILES = 20
MAX_FILE_SIZE = 1024 * 1024  # 1MB
MAX_ZIP_SIZE = 200 * 1024 * 1024  # 200MB for ZIP archives
MAX_FILES_IN_ZIP = 1000  # Maximum files to extract from ZIP
URL_FETCH_TIMEOUT = 10  # seconds
MAX_URL_CONTENT_SIZE = 1024 * 1024  # 1MB

# Supported song file extensions
SONG_EXTENSIONS = {".cho", ".crd", ".chopro", ".txt", ".xml", ".onsong"}


def is_zip_file(content: bytes) -> bool:
    """Check if content is a ZIP archive by magic bytes."""
    return content[:4] == b"PK\x03\x04"


def extract_zip_files(
    zip_content: bytes, zip_filename: str
) -> list[tuple[str, bytes, str | None]]:
    """Extract song files from a ZIP archive.

    Returns list of tuples: (filename, content, error)
    """
    results: list[tuple[str, bytes, str | None]] = []

    try:
        with zipfile.ZipFile(BytesIO(zip_content), "r") as zf:
            # Get list of files (exclude directories and hidden files)
            file_list = [
                name
                for name in zf.namelist()
                if not name.endswith("/")
                and not name.startswith("__MACOSX/")
                and not name.split("/")[-1].startswith(".")
            ]

            # Check file count limit
            if len(file_list) > MAX_FILES_IN_ZIP:
                file_list = file_list[:MAX_FILES_IN_ZIP]

            for name in file_list:
                # Check if it's a supported song file
                ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
                if ext not in SONG_EXTENSIONS:
                    continue

                try:
                    content = zf.read(name)
                    # Check individual file size
                    if len(content) > MAX_FILE_SIZE:
                        results.append(
                            (name, b"", f"File exceeds maximum size of {MAX_FILE_SIZE // 1024}KB")
                        )
                    else:
                        results.append((name, content, None))
                except Exception as e:
                    results.append((name, b"", f"Failed to extract: {str(e)}"))

    except zipfile.BadZipFile:
        results.append((zip_filename, b"", "Invalid ZIP archive"))
    except Exception as e:
        results.append((zip_filename, b"", f"Failed to read ZIP: {str(e)}"))

    return results


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_import(
    files: list[UploadFile],
    db: AsyncSession = Depends(get_db),
) -> ImportPreviewResponse:
    """Parse uploaded files and return preview data.

    This endpoint does NOT save anything to the database.
    Use /confirm to save selected songs.

    Also checks for duplicates and includes existing song info.

    Supports ZIP archives containing multiple song files.

    Limits:
    - Maximum 20 files per request (or 50 files from a ZIP)
    - Maximum 1MB per file, 10MB for ZIP archives
    """
    # Validate file count
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_FILES} files allowed per request",
        )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided",
        )

    # Collect all files to parse (including extracted from ZIPs)
    files_to_parse: list[tuple[str, bytes]] = []

    for file in files:
        # Read file content
        try:
            content = await file.read()
        except Exception as e:
            files_to_parse.append((file.filename or "unknown", b""))
            continue

        filename = file.filename or "unknown"

        # Check if it's a ZIP archive
        if is_zip_file(content):
            # Check ZIP size limit
            if len(content) > MAX_ZIP_SIZE:
                files_to_parse.append(
                    (filename, b"")
                )  # Will be handled as error below
                continue

            # Extract files from ZIP
            extracted = extract_zip_files(content, filename)
            for extracted_name, extracted_content, error in extracted:
                if error:
                    # Store with empty content to indicate error
                    files_to_parse.append((f"{filename}/{extracted_name}", b""))
                else:
                    files_to_parse.append((f"{filename}/{extracted_name}", extracted_content))
        else:
            files_to_parse.append((filename, content))

    parsed_songs: list[ParsedSong] = []
    successful = 0
    failed = 0

    for filename, content in files_to_parse:
        # Handle files that failed to read or extract
        if len(content) == 0:
            parsed_songs.append(
                ParsedSong(
                    file_name=filename,
                    detected_format="unknown",
                    success=False,
                    error="Failed to read file",
                )
            )
            failed += 1
            continue

        # Check file size
        if len(content) > MAX_FILE_SIZE:
            parsed_songs.append(
                ParsedSong(
                    file_name=filename,
                    detected_format="unknown",
                    success=False,
                    error=f"File exceeds maximum size of {MAX_FILE_SIZE // 1024}KB",
                )
            )
            failed += 1
            continue

        # Parse file
        result = detect_and_parse(content, filename)

        if result.success:
            parsed_songs.append(
                ParsedSong(
                    file_name=filename,
                    detected_format=result.detected_format,
                    success=True,
                    song_data=result.song_data,
                )
            )
            successful += 1
        else:
            parsed_songs.append(
                ParsedSong(
                    file_name=filename,
                    detected_format=result.detected_format,
                    success=False,
                    error=result.error,
                )
            )
            failed += 1

    # Check for duplicates in successfully parsed songs
    songs_to_check = [
        SongCheck(name=ps.song_data.name, artist=ps.song_data.artist)
        for ps in parsed_songs
        if ps.success and ps.song_data
    ]

    if songs_to_check:
        duplicates = await find_duplicates(db, songs_to_check)

        # Create a mapping of (name, artist) -> existing song for quick lookup
        duplicate_map: dict[tuple[str, str | None], ExistingSongSummary] = {
            (d.name.lower(), d.artist.lower() if d.artist else None): d.existing_song
            for d in duplicates
        }

        # Update parsed songs with duplicate info
        for ps in parsed_songs:
            if ps.success and ps.song_data:
                key = (
                    ps.song_data.name.lower(),
                    ps.song_data.artist.lower() if ps.song_data.artist else None,
                )
                if key in duplicate_map:
                    ps.duplicate = duplicate_map[key]

    return ImportPreviewResponse(
        total_files=len(files_to_parse),
        successful=successful,
        failed=failed,
        songs=parsed_songs,
    )


@router.post("/preview-url", response_model=ImportPreviewResponse)
async def preview_url_import(
    request: UrlImportRequest,
    db: AsyncSession = Depends(get_db),
) -> ImportPreviewResponse:
    """Fetch content from a URL and return preview data.

    This endpoint does NOT save anything to the database.
    Use /confirm to save selected songs.

    Limits:
    - Maximum 1MB content size
    - 10 second timeout
    """
    url = str(request.url)

    # Extract filename from URL path
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.rsplit("/", 1)
    filename = path_parts[-1] if len(path_parts) > 1 and path_parts[-1] else "url_import"

    # Fetch URL content
    try:
        async with httpx.AsyncClient(
            timeout=URL_FETCH_TIMEOUT,
            follow_redirects=True,
            max_redirects=5,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > MAX_URL_CONTENT_SIZE:
                return ImportPreviewResponse(
                    total_files=1,
                    successful=0,
                    failed=1,
                    songs=[
                        ParsedSong(
                            file_name=filename,
                            detected_format="unknown",
                            success=False,
                            error=f"Content exceeds maximum size of {MAX_URL_CONTENT_SIZE // 1024}KB",
                        )
                    ],
                )

            content = response.content

            # Double-check actual content size
            if len(content) > MAX_URL_CONTENT_SIZE:
                return ImportPreviewResponse(
                    total_files=1,
                    successful=0,
                    failed=1,
                    songs=[
                        ParsedSong(
                            file_name=filename,
                            detected_format="unknown",
                            success=False,
                            error=f"Content exceeds maximum size of {MAX_URL_CONTENT_SIZE // 1024}KB",
                        )
                    ],
                )

    except httpx.TimeoutException:
        return ImportPreviewResponse(
            total_files=1,
            successful=0,
            failed=1,
            songs=[
                ParsedSong(
                    file_name=filename,
                    detected_format="unknown",
                    success=False,
                    error="Request timed out",
                )
            ],
        )
    except httpx.HTTPStatusError as e:
        return ImportPreviewResponse(
            total_files=1,
            successful=0,
            failed=1,
            songs=[
                ParsedSong(
                    file_name=filename,
                    detected_format="unknown",
                    success=False,
                    error=f"HTTP error: {e.response.status_code}",
                )
            ],
        )
    except httpx.RequestError as e:
        return ImportPreviewResponse(
            total_files=1,
            successful=0,
            failed=1,
            songs=[
                ParsedSong(
                    file_name=filename,
                    detected_format="unknown",
                    success=False,
                    error=f"Failed to fetch URL: {str(e)}",
                )
            ],
        )

    # Parse the content
    result = detect_and_parse(content, filename)

    if result.success:
        parsed_song = ParsedSong(
            file_name=filename,
            detected_format=result.detected_format,
            success=True,
            song_data=result.song_data,
        )

        # Check for duplicates
        if result.song_data:
            duplicates = await find_duplicates(
                db,
                [SongCheck(name=result.song_data.name, artist=result.song_data.artist)],
            )
            if duplicates:
                parsed_song.duplicate = duplicates[0].existing_song

        return ImportPreviewResponse(
            total_files=1,
            successful=1,
            failed=0,
            songs=[parsed_song],
        )
    else:
        return ImportPreviewResponse(
            total_files=1,
            successful=0,
            failed=1,
            songs=[
                ParsedSong(
                    file_name=filename,
                    detected_format=result.detected_format,
                    success=False,
                    error=result.error,
                )
            ],
        )


@router.post("/confirm", response_model=ImportConfirmResponse)
async def confirm_import(
    request: ImportConfirmRequest,
    db: AsyncSession = Depends(get_db),
) -> ImportConfirmResponse:
    """Save selected songs from preview to the database.

    Each song can have an action:
    - CREATE: Create as new song (default)
    - MERGE: Update existing song with new data (requires existing_song_id)
    - SKIP: Don't import this song
    """
    from app.schemas.import_song import ImportAction

    if not request.songs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No songs provided",
        )

    result_songs: list[Song] = []
    created_count = 0
    merged_count = 0
    skipped_count = 0

    for item in request.songs:
        song_data = item.song_data

        if item.action == ImportAction.SKIP:
            skipped_count += 1
            continue

        if item.action == ImportAction.MERGE:
            if not item.existing_song_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="existing_song_id required for merge action",
                )

            # Fetch existing song
            existing = await db.get(Song, item.existing_song_id)
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Song {item.existing_song_id} not found",
                )

            # Merge: update existing song with new data
            if song_data.name:
                existing.name = song_data.name
            if song_data.artist is not None:
                existing.artist = song_data.artist
            if song_data.url is not None:
                existing.url = song_data.url
            if song_data.original_key is not None:
                existing.original_key = song_data.original_key.value
            if song_data.preferred_key is not None:
                existing.preferred_key = song_data.preferred_key.value
            if song_data.tempo_bpm is not None:
                existing.tempo_bpm = song_data.tempo_bpm
            if song_data.mood is not None:
                existing.mood = song_data.mood.value
            if song_data.themes is not None:
                existing.themes = [t.value for t in song_data.themes]
            if song_data.lyrics is not None:
                existing.lyrics = song_data.lyrics
            if song_data.chordpro_chart is not None:
                existing.chordpro_chart = song_data.chordpro_chart
            if song_data.min_band is not None:
                existing.min_band = song_data.min_band
            if song_data.notes is not None:
                existing.notes = song_data.notes

            result_songs.append(existing)
            merged_count += 1

        else:  # CREATE (default)
            song = Song(
                name=song_data.name,
                artist=song_data.artist,
                url=song_data.url,
                original_key=song_data.original_key.value if song_data.original_key else None,
                preferred_key=song_data.preferred_key.value if song_data.preferred_key else None,
                tempo_bpm=song_data.tempo_bpm,
                mood=song_data.mood.value if song_data.mood else None,
                themes=[t.value for t in song_data.themes] if song_data.themes else None,
                lyrics=song_data.lyrics,
                chordpro_chart=song_data.chordpro_chart,
                min_band=song_data.min_band,
                notes=song_data.notes,
            )
            db.add(song)
            result_songs.append(song)
            created_count += 1

    await db.commit()

    # Refresh all songs to get their IDs
    for song in result_songs:
        await db.refresh(song)

    return ImportConfirmResponse(
        created_count=created_count,
        merged_count=merged_count,
        skipped_count=skipped_count,
        songs=[SongResponse.model_validate(song) for song in result_songs],
    )
