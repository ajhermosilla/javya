package dev.cronova.javya.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import androidx.room.Update
import dev.cronova.javya.data.local.database.entity.SetlistEntity
import dev.cronova.javya.data.local.database.entity.SetlistSongEntity
import dev.cronova.javya.data.local.database.entity.SyncStatus
import kotlinx.coroutines.flow.Flow

@Dao
interface SetlistDao {

    @Query("SELECT * FROM setlists WHERE sync_status != :deletedStatus ORDER BY service_date DESC, name ASC")
    fun getAllSetlists(deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE): Flow<List<SetlistEntity>>

    @Query("SELECT * FROM setlists WHERE id = :id")
    fun getSetlistById(id: String): Flow<SetlistEntity?>

    @Query("SELECT * FROM setlists WHERE id = :id")
    suspend fun getSetlistByIdOnce(id: String): SetlistEntity?

    @Query("""
        SELECT * FROM setlists
        WHERE sync_status != :deletedStatus
        AND name LIKE '%' || :query || '%'
        ORDER BY service_date DESC, name ASC
    """)
    fun searchSetlists(
        query: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<SetlistEntity>>

    @Query("""
        SELECT * FROM setlists
        WHERE sync_status != :deletedStatus
        AND (:eventType IS NULL OR event_type = :eventType)
        ORDER BY service_date DESC, name ASC
    """)
    fun filterSetlists(
        eventType: String?,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<SetlistEntity>>

    @Query("""
        SELECT * FROM setlists
        WHERE sync_status != :deletedStatus
        AND service_date BETWEEN :startDate AND :endDate
        ORDER BY service_date ASC
    """)
    fun getSetlistsByDateRange(
        startDate: String,
        endDate: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<SetlistEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(setlist: SetlistEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(setlists: List<SetlistEntity>)

    @Update
    suspend fun update(setlist: SetlistEntity)

    @Query("DELETE FROM setlists WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("UPDATE setlists SET sync_status = :status WHERE id = :id")
    suspend fun updateSyncStatus(id: String, status: SyncStatus)

    @Query("SELECT * FROM setlists WHERE sync_status != :synced")
    suspend fun getPendingChanges(synced: SyncStatus = SyncStatus.SYNCED): List<SetlistEntity>

    // Setlist Songs
    @Query("SELECT * FROM setlist_songs WHERE setlist_id = :setlistId ORDER BY position ASC")
    fun getSetlistSongs(setlistId: String): Flow<List<SetlistSongEntity>>

    @Query("SELECT * FROM setlist_songs WHERE setlist_id = :setlistId ORDER BY position ASC")
    suspend fun getSetlistSongsOnce(setlistId: String): List<SetlistSongEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSetlistSong(setlistSong: SetlistSongEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSetlistSongs(setlistSongs: List<SetlistSongEntity>)

    @Query("DELETE FROM setlist_songs WHERE setlist_id = :setlistId")
    suspend fun deleteSetlistSongs(setlistId: String)

    @Query("DELETE FROM setlist_songs WHERE id = :id")
    suspend fun deleteSetlistSongById(id: String)

    @Query("UPDATE setlist_songs SET position = :position WHERE id = :id")
    suspend fun updateSetlistSongPosition(id: String, position: Int)

    @Transaction
    suspend fun replaceSetlistSongs(setlistId: String, songs: List<SetlistSongEntity>) {
        deleteSetlistSongs(setlistId)
        insertSetlistSongs(songs)
    }
}
