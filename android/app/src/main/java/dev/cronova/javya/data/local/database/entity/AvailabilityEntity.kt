package dev.cronova.javya.data.local.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Room entity for user availability on specific dates.
 */
@Entity(
    tableName = "availability",
    foreignKeys = [
        ForeignKey(
            entity = UserEntity::class,
            parentColumns = ["id"],
            childColumns = ["user_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["user_id"]),
        Index(value = ["date"])
    ]
)
data class AvailabilityEntity(
    @PrimaryKey
    val id: String,

    @ColumnInfo(name = "user_id")
    val userId: String,

    val date: String, // ISO format: YYYY-MM-DD

    val status: String, // AvailabilityStatus value

    val note: String? = null,

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
