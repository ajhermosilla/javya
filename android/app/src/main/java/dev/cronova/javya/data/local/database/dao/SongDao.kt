package dev.cronova.javya.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import dev.cronova.javya.data.local.database.entity.SongEntity
import dev.cronova.javya.data.local.database.entity.SyncStatus
import kotlinx.coroutines.flow.Flow

@Dao
interface SongDao {

    @Query("SELECT * FROM songs WHERE sync_status != :deletedStatus ORDER BY name ASC")
    fun getAllSongs(deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE): Flow<List<SongEntity>>

    @Query("SELECT * FROM songs WHERE sync_status != :deletedStatus ORDER BY name ASC LIMIT :limit OFFSET :offset")
    suspend fun getSongsPaginated(
        limit: Int,
        offset: Int,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): List<SongEntity>

    @Query("SELECT * FROM songs WHERE id = :id")
    fun getSongById(id: String): Flow<SongEntity?>

    @Query("SELECT * FROM songs WHERE id = :id")
    suspend fun getSongByIdOnce(id: String): SongEntity?

    @Query("""
        SELECT * FROM songs
        WHERE sync_status != :deletedStatus
        AND (name LIKE '%' || :query || '%' OR artist LIKE '%' || :query || '%')
        ORDER BY name ASC
    """)
    fun searchSongs(
        query: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<SongEntity>>

    @Query("""
        SELECT * FROM songs
        WHERE sync_status != :deletedStatus
        AND (:key IS NULL OR original_key = :key OR preferred_key = :key)
        AND (:mood IS NULL OR mood = :mood)
        ORDER BY name ASC
    """)
    fun filterSongs(
        key: String?,
        mood: String?,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<SongEntity>>

    @Query("SELECT COUNT(*) FROM songs WHERE sync_status != :deletedStatus")
    suspend fun getSongCount(deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(song: SongEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(songs: List<SongEntity>)

    @Update
    suspend fun update(song: SongEntity)

    @Query("DELETE FROM songs WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("UPDATE songs SET sync_status = :status WHERE id = :id")
    suspend fun updateSyncStatus(id: String, status: SyncStatus)

    @Query("SELECT * FROM songs WHERE sync_status != :synced")
    suspend fun getPendingChanges(synced: SyncStatus = SyncStatus.SYNCED): List<SongEntity>

    @Query("DELETE FROM songs WHERE sync_status = :deletedStatus")
    suspend fun deletePendingDeletes(deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE)
}
