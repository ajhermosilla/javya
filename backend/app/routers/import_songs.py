"""Router for song import endpoints."""

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
URL_FETCH_TIMEOUT = 10  # seconds
MAX_URL_CONTENT_SIZE = 1024 * 1024  # 1MB


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_import(
    files: list[UploadFile],
    db: AsyncSession = Depends(get_db),
) -> ImportPreviewResponse:
    """Parse uploaded files and return preview data.

    This endpoint does NOT save anything to the database.
    Use /confirm to save selected songs.

    Also checks for duplicates and includes existing song info.

    Limits:
    - Maximum 20 files per request
    - Maximum 1MB per file
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

    parsed_songs: list[ParsedSong] = []
    successful = 0
    failed = 0

    for file in files:
        # Read file content
        try:
            content = await file.read()
        except Exception as e:
            parsed_songs.append(
                ParsedSong(
                    file_name=file.filename or "unknown",
                    detected_format="unknown",
                    success=False,
                    error=f"Failed to read file: {str(e)}",
                )
            )
            failed += 1
            continue

        # Check file size
        if len(content) > MAX_FILE_SIZE:
            parsed_songs.append(
                ParsedSong(
                    file_name=file.filename or "unknown",
                    detected_format="unknown",
                    success=False,
                    error=f"File exceeds maximum size of {MAX_FILE_SIZE // 1024}KB",
                )
            )
            failed += 1
            continue

        # Parse file
        result = detect_and_parse(content, file.filename or "unknown")

        if result.success:
            parsed_songs.append(
                ParsedSong(
                    file_name=file.filename or "unknown",
                    detected_format=result.detected_format,
                    success=True,
                    song_data=result.song_data,
                )
            )
            successful += 1
        else:
            parsed_songs.append(
                ParsedSong(
                    file_name=file.filename or "unknown",
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
        total_files=len(files),
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

    Pass the song_data objects from the preview response
    for the songs you want to import.
    """
    if not request.songs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No songs provided",
        )

    saved_songs: list[Song] = []

    for song_data in request.songs:
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
        saved_songs.append(song)

    await db.commit()

    # Refresh all songs to get their IDs
    for song in saved_songs:
        await db.refresh(song)

    return ImportConfirmResponse(
        saved_count=len(saved_songs),
        songs=[SongResponse.model_validate(song) for song in saved_songs],
    )
