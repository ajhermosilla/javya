package dev.cronova.javya.data.local.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Room entity for team member assignments to setlists.
 */
@Entity(
    tableName = "setlist_assignments",
    foreignKeys = [
        ForeignKey(
            entity = SetlistEntity::class,
            parentColumns = ["id"],
            childColumns = ["setlist_id"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = UserEntity::class,
            parentColumns = ["id"],
            childColumns = ["user_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["setlist_id"]),
        Index(value = ["user_id"])
    ]
)
data class SetlistAssignmentEntity(
    @PrimaryKey
    val id: String,

    @ColumnInfo(name = "setlist_id")
    val setlistId: String,

    @ColumnInfo(name = "user_id")
    val userId: String,

    @ColumnInfo(name = "service_role")
    val serviceRole: String, // ServiceRole value

    val notes: String? = null,

    val confirmed: Boolean = false,

    @ColumnInfo(name = "created_at")
    val createdAt: String,

    @ColumnInfo(name = "updated_at")
    val updatedAt: String,

    // Denormalized user info for offline display
    @ColumnInfo(name = "user_name")
    val userName: String? = null,

    @ColumnInfo(name = "user_email")
    val userEmail: String? = null,

    // Sync metadata
    @ColumnInfo(name = "sync_status")
    val syncStatus: SyncStatus = SyncStatus.SYNCED,

    @ColumnInfo(name = "locally_modified_at")
    val locallyModifiedAt: Long? = null
)
