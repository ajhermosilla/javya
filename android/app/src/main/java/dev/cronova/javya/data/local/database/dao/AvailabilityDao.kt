package dev.cronova.javya.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import dev.cronova.javya.data.local.database.entity.AvailabilityEntity
import dev.cronova.javya.data.local.database.entity.AvailabilityPatternEntity
import dev.cronova.javya.data.local.database.entity.SyncStatus
import kotlinx.coroutines.flow.Flow

@Dao
interface AvailabilityDao {

    // Availability entries
    @Query("""
        SELECT * FROM availability
        WHERE user_id = :userId
        AND sync_status != :deletedStatus
        AND date BETWEEN :startDate AND :endDate
        ORDER BY date ASC
    """)
    fun getAvailabilityByDateRange(
        userId: String,
        startDate: String,
        endDate: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<AvailabilityEntity>>

    @Query("""
        SELECT * FROM availability
        WHERE sync_status != :deletedStatus
        AND date BETWEEN :startDate AND :endDate
        ORDER BY date ASC, user_id ASC
    """)
    fun getTeamAvailabilityByDateRange(
        startDate: String,
        endDate: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<AvailabilityEntity>>

    @Query("SELECT * FROM availability WHERE id = :id")
    suspend fun getAvailabilityById(id: String): AvailabilityEntity?

    @Query("SELECT * FROM availability WHERE user_id = :userId AND date = :date")
    suspend fun getAvailabilityByUserAndDate(userId: String, date: String): AvailabilityEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(availability: AvailabilityEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(availability: List<AvailabilityEntity>)

    @Update
    suspend fun update(availability: AvailabilityEntity)

    @Query("DELETE FROM availability WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("UPDATE availability SET sync_status = :status WHERE id = :id")
    suspend fun updateSyncStatus(id: String, status: SyncStatus)

    @Query("SELECT * FROM availability WHERE sync_status != :synced")
    suspend fun getPendingChanges(synced: SyncStatus = SyncStatus.SYNCED): List<AvailabilityEntity>

    // Availability patterns
    @Query("""
        SELECT * FROM availability_patterns
        WHERE user_id = :userId
        AND sync_status != :deletedStatus
        ORDER BY day_of_week ASC
    """)
    fun getPatternsByUser(
        userId: String,
        deletedStatus: SyncStatus = SyncStatus.PENDING_DELETE
    ): Flow<List<AvailabilityPatternEntity>>

    @Query("SELECT * FROM availability_patterns WHERE id = :id")
    suspend fun getPatternById(id: String): AvailabilityPatternEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPattern(pattern: AvailabilityPatternEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPatterns(patterns: List<AvailabilityPatternEntity>)

    @Update
    suspend fun updatePattern(pattern: AvailabilityPatternEntity)

    @Query("DELETE FROM availability_patterns WHERE id = :id")
    suspend fun deletePatternById(id: String)

    @Query("UPDATE availability_patterns SET sync_status = :status WHERE id = :id")
    suspend fun updatePatternSyncStatus(id: String, status: SyncStatus)

    @Query("SELECT * FROM availability_patterns WHERE sync_status != :synced")
    suspend fun getPendingPatternChanges(synced: SyncStatus = SyncStatus.SYNCED): List<AvailabilityPatternEntity>
}
