package dev.cronova.javya.data.local.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Room entity for tracking sync metadata.
 */
@Entity(tableName = "sync_metadata")
data class SyncMetadataEntity(
    @PrimaryKey
    @ColumnInfo(name = "entity_type")
    val entityType: String, // "songs", "setlists", "availability", etc.

    @ColumnInfo(name = "last_sync_time")
    val lastSyncTime: Long, // Unix timestamp in milliseconds

    @ColumnInfo(name = "last_sync_success")
    val lastSyncSuccess: Boolean = true,

    @ColumnInfo(name = "last_error")
    val lastError: String? = null
)
