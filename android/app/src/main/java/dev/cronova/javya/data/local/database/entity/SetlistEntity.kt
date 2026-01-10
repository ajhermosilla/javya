package dev.cronova.javya.data.local.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Room entity for setlists.
 */
@Entity(tableName = "setlists")
data class SetlistEntity(
    @PrimaryKey
    val id: String,

    val name: String,

    val description: String? = null,

    @ColumnInfo(name = "service_date")
    val serviceDate: String? = null,

    @ColumnInfo(name = "event_type")
    val eventType: String? = null,

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
