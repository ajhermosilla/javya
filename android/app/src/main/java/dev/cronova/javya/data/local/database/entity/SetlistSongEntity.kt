package dev.cronova.javya.data.local.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Room entity for setlist-song associations with ordering.
 */
@Entity(
    tableName = "setlist_songs",
    foreignKeys = [
        ForeignKey(
            entity = SetlistEntity::class,
            parentColumns = ["id"],
            childColumns = ["setlist_id"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = SongEntity::class,
            parentColumns = ["id"],
            childColumns = ["song_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["setlist_id"]),
        Index(value = ["song_id"])
    ]
)
data class SetlistSongEntity(
    @PrimaryKey
    val id: String,

    @ColumnInfo(name = "setlist_id")
    val setlistId: String,

    @ColumnInfo(name = "song_id")
    val songId: String,

    val position: Int,

    val notes: String? = null,

    // Sync metadata
    @ColumnInfo(name = "sync_status")
    val syncStatus: SyncStatus = SyncStatus.SYNCED
)
