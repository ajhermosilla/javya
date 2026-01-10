package dev.cronova.javya.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import dev.cronova.javya.data.local.database.entity.UserEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface UserDao {

    @Query("SELECT * FROM users ORDER BY name ASC")
    fun getAllUsers(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    fun getUserById(id: String): Flow<UserEntity?>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserByIdOnce(id: String): UserEntity?

    @Query("SELECT * FROM users WHERE is_active = 1 ORDER BY name ASC")
    fun getActiveUsers(): Flow<List<UserEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(users: List<UserEntity>)

    @Query("DELETE FROM users WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}
