package dev.cronova.javya.data.local.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Room entity for recurring availability patterns.
 */
@Entity(
    tableName = "availability_patterns",
    foreignKeys = [
        ForeignKey(
            entity = UserEntity::class,
            parentColumns = ["id"],
            childColumns = ["user_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["user_id"])
    ]
)
data class AvailabilityPatternEntity(
    @PrimaryKey
    val id: String,

    @ColumnInfo(name = "user_id")
    val userId: String,

    @ColumnInfo(name = "pattern_type")
    val patternType: String, // PatternType value

    @ColumnInfo(name = "day_of_week")
    val dayOfWeek: Int, // 0 = Monday, 6 = Sunday

    val status: String, // AvailabilityStatus value

    @ColumnInfo(name = "start_date")
    val startDate: String? = null,

    @ColumnInfo(name = "end_date")
    val endDate: String? = null,

    @ColumnInfo(name = "is_active")
    val isActive: Boolean = true,

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
