package dev.cronova.javya.util

import dev.cronova.javya.data.local.database.entity.*
import java.time.OffsetDateTime
import java.time.LocalDate
import java.util.UUID

/**
 * Factory object for creating test data in instrumented tests.
 */
object TestData {

    private fun now(): String = OffsetDateTime.now().toString()

    // ==================== Users ====================

    fun createUserEntity(
        id: String = UUID.randomUUID().toString(),
        email: String = "test@example.com",
        name: String = "Test User",
        role: String = "member",
        isActive: Boolean = true
    ) = UserEntity(
        id = id,
        email = email,
        name = name,
        role = role,
        isActive = isActive,
        createdAt = now(),
        updatedAt = now()
    )

    // ==================== Songs ====================

    fun createSongEntity(
        id: String = UUID.randomUUID().toString(),
        name: String = "Amazing Grace",
        artist: String? = "John Newton",
        url: String? = null,
        originalKey: String? = "G",
        preferredKey: String? = null,
        tempoBpm: Int? = 72,
        mood: String? = "reflective",
        themes: String? = "[\"grace\",\"worship\"]",
        lyrics: String? = "Amazing grace, how sweet the sound",
        chordproChart: String? = "[G]Amazing [C]grace",
        minBand: String? = null,
        notes: String? = null,
        syncStatus: SyncStatus = SyncStatus.SYNCED
    ) = SongEntity(
        id = id,
        name = name,
        artist = artist,
        url = url,
        originalKey = originalKey,
        preferredKey = preferredKey,
        tempoBpm = tempoBpm,
        mood = mood,
        themes = themes,
        lyrics = lyrics,
        chordproChart = chordproChart,
        minBand = minBand,
        notes = notes,
        createdAt = now(),
        updatedAt = now(),
        syncStatus = syncStatus
    )

    // ==================== Setlists ====================

    fun createSetlistEntity(
        id: String = UUID.randomUUID().toString(),
        name: String = "Sunday Morning Worship",
        description: String? = null,
        serviceDate: String? = LocalDate.now().plusDays(7).toString(),
        eventType: String? = "sunday",
        syncStatus: SyncStatus = SyncStatus.SYNCED
    ) = SetlistEntity(
        id = id,
        name = name,
        description = description,
        serviceDate = serviceDate,
        eventType = eventType,
        createdAt = now(),
        updatedAt = now(),
        syncStatus = syncStatus
    )

    fun createSetlistSongEntity(
        id: String = UUID.randomUUID().toString(),
        setlistId: String = UUID.randomUUID().toString(),
        songId: String = UUID.randomUUID().toString(),
        position: Int = 0,
        notes: String? = null,
        syncStatus: SyncStatus = SyncStatus.SYNCED
    ) = SetlistSongEntity(
        id = id,
        setlistId = setlistId,
        songId = songId,
        position = position,
        notes = notes,
        syncStatus = syncStatus
    )

    // ==================== Availability ====================

    fun createAvailabilityEntity(
        id: String = UUID.randomUUID().toString(),
        userId: String = UUID.randomUUID().toString(),
        date: String = LocalDate.now().toString(),
        status: String = "available",
        note: String? = null,
        syncStatus: SyncStatus = SyncStatus.SYNCED
    ) = AvailabilityEntity(
        id = id,
        userId = userId,
        date = date,
        status = status,
        note = note,
        createdAt = now(),
        updatedAt = now(),
        syncStatus = syncStatus
    )

    fun createAvailabilityPatternEntity(
        id: String = UUID.randomUUID().toString(),
        userId: String = UUID.randomUUID().toString(),
        patternType: String = "weekly",
        dayOfWeek: Int = 0,
        status: String = "available",
        startDate: String? = LocalDate.now().toString(),
        endDate: String? = null,
        isActive: Boolean = true,
        note: String? = null,
        syncStatus: SyncStatus = SyncStatus.SYNCED
    ) = AvailabilityPatternEntity(
        id = id,
        userId = userId,
        patternType = patternType,
        dayOfWeek = dayOfWeek,
        status = status,
        startDate = startDate,
        endDate = endDate,
        isActive = isActive,
        note = note,
        createdAt = now(),
        updatedAt = now(),
        syncStatus = syncStatus
    )

    // ==================== Assignments ====================

    fun createSetlistAssignmentEntity(
        id: String = UUID.randomUUID().toString(),
        setlistId: String = UUID.randomUUID().toString(),
        userId: String = UUID.randomUUID().toString(),
        serviceRole: String = "worship_leader",
        notes: String? = null,
        confirmed: Boolean = false,
        userName: String? = null,
        userEmail: String? = null,
        syncStatus: SyncStatus = SyncStatus.SYNCED
    ) = SetlistAssignmentEntity(
        id = id,
        setlistId = setlistId,
        userId = userId,
        serviceRole = serviceRole,
        notes = notes,
        confirmed = confirmed,
        userName = userName,
        userEmail = userEmail,
        createdAt = now(),
        updatedAt = now(),
        syncStatus = syncStatus
    )

    // ==================== Sync Metadata ====================

    fun createSyncMetadataEntity(
        entityType: String = "songs",
        lastSyncedAt: String = now()
    ) = SyncMetadataEntity(
        entityType = entityType,
        lastSyncedAt = lastSyncedAt
    )

    // ==================== Bulk Data ====================

    fun createSongList(count: Int = 5): List<SongEntity> =
        (1..count).map { i ->
            createSongEntity(
                id = UUID.randomUUID().toString(),
                name = "Song $i",
                artist = "Artist $i"
            )
        }

    fun createSetlistWithSongs(songCount: Int = 3): Pair<SetlistEntity, List<SetlistSongEntity>> {
        val setlist = createSetlistEntity()
        val songs = (0 until songCount).map { i ->
            createSetlistSongEntity(
                setlistId = setlist.id,
                songId = UUID.randomUUID().toString(),
                position = i
            )
        }
        return setlist to songs
    }
}
