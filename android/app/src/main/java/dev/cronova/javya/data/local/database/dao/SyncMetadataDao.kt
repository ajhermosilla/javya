package dev.cronova.javya.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import dev.cronova.javya.data.local.database.entity.SyncMetadataEntity

@Dao
interface SyncMetadataDao {

    @Query("SELECT * FROM sync_metadata WHERE entity_type = :entityType")
    suspend fun getMetadata(entityType: String): SyncMetadataEntity?

    @Query("SELECT last_sync_time FROM sync_metadata WHERE entity_type = :entityType")
    suspend fun getLastSyncTime(entityType: String): Long?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(metadata: SyncMetadataEntity)

    @Query("UPDATE sync_metadata SET last_sync_time = :timestamp, last_sync_success = :success, last_error = :error WHERE entity_type = :entityType")
    suspend fun updateSyncResult(entityType: String, timestamp: Long, success: Boolean, error: String? = null)

    @Query("DELETE FROM sync_metadata")
    suspend fun deleteAll()
}
