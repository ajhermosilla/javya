package dev.cronova.javya.data.local.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Room entity for songs.
 */
@Entity(tableName = "songs")
data class SongEntity(
    @PrimaryKey
    val id: String,

    val name: String,

    val artist: String? = null,

    val url: String? = null,

    @ColumnInfo(name = "original_key")
    val originalKey: String? = null,

    @ColumnInfo(name = "preferred_key")
    val preferredKey: String? = null,

    @ColumnInfo(name = "tempo_bpm")
    val tempoBpm: Int? = null,

    val mood: String? = null,

    // Stored as JSON array string
    val themes: String? = null,

    val lyrics: String? = null,

    @ColumnInfo(name = "chordpro_chart")
    val chordproChart: String? = null,

    // Stored as JSON array string
    @ColumnInfo(name = "min_band")
    val minBand: String? = null,

    val notes: String? = null,

    @ColumnInfo(name = "created_at")
    val createdAt: String,

    @ColumnInfo(name = "updated_at")
    val updatedAt: String,

    // Sync metadata
    @ColumnInfo(name = "sync_status")
    val syncStatus: SyncStatus = SyncStatus.SYNCED,

    @ColumnInfo(name = "locally_modified_at")
    val locallyModifiedAt: Long? = null
)
