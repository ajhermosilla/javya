package dev.cronova.javya.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import dev.cronova.javya.data.local.database.entity.SetlistAssignmentEntity
import dev.cronova.javya.data.local.database.entity.SyncStatus
import kotlinx.coroutines.flow.Flow

@Dao
interface SetlistAssignmentDao {

    @Query("""
        SELECT * FROM setlist_assignments
        WHERE setlist_id = :setlistId
        AND sync_status != :deletedStatus
        ORDER BY service_role ASC
    """)
    fun getAssignmentsBySetlist(
        setlistId: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<SetlistAssignmentEntity>>

    @Query("""
        SELECT * FROM setlist_assignments
        WHERE user_id = :userId
        AND sync_status != :deletedStatus
        ORDER BY created_at DESC
    """)
    fun getAssignmentsByUser(
        userId: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<SetlistAssignmentEntity>>

    @Query("SELECT * FROM setlist_assignments WHERE id = :id")
    suspend fun getAssignmentById(id: String): SetlistAssignmentEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(assignment: SetlistAssignmentEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(assignments: List<SetlistAssignmentEntity>)

    @Update
    suspend fun update(assignment: SetlistAssignmentEntity)

    @Query("DELETE FROM setlist_assignments WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM setlist_assignments WHERE setlist_id = :setlistId")
    suspend fun deleteBySetlist(setlistId: String)

    @Query("UPDATE setlist_assignments SET confirmed = :confirmed, sync_status = :status WHERE id = :id")
    suspend fun updateConfirmation(id: String, confirmed: Boolean, status: SyncStatus = SyncStatus.PENDING_UPDATE)

    @Query("UPDATE setlist_assignments SET sync_status = :status WHERE id = :id")
    suspend fun updateSyncStatus(id: String, status: SyncStatus)

    @Query("SELECT * FROM setlist_assignments WHERE sync_status != :synced")
    suspend fun getPendingChanges(synced: SyncStatus = SyncStatus.SYNCED): List<SetlistAssignmentEntity>
}
