package dev.cronova.javya.data.local.database

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import dev.cronova.javya.data.local.database.converter.Converters
import dev.cronova.javya.data.local.database.dao.AvailabilityDao
import dev.cronova.javya.data.local.database.dao.SetlistAssignmentDao
import dev.cronova.javya.data.local.database.dao.SetlistDao
import dev.cronova.javya.data.local.database.dao.SongDao
import dev.cronova.javya.data.local.database.dao.SyncMetadataDao
import dev.cronova.javya.data.local.database.dao.UserDao
import dev.cronova.javya.data.local.database.entity.AvailabilityEntity
import dev.cronova.javya.data.local.database.entity.AvailabilityPatternEntity
import dev.cronova.javya.data.local.database.entity.SetlistAssignmentEntity
import dev.cronova.javya.data.local.database.entity.SetlistEntity
import dev.cronova.javya.data.local.database.entity.SetlistSongEntity
import dev.cronova.javya.data.local.database.entity.SongEntity
import dev.cronova.javya.data.local.database.entity.SyncMetadataEntity
import dev.cronova.javya.data.local.database.entity.UserEntity

@Database(
    entities = [
        SongEntity::class,
        SetlistEntity::class,
        SetlistSongEntity::class,
        UserEntity::class,
        AvailabilityEntity::class,
        AvailabilityPatternEntity::class,
        SetlistAssignmentEntity::class,
        SyncMetadataEntity::class
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class JavyaDatabase : RoomDatabase() {
    abstract fun songDao(): SongDao
    abstract fun setlistDao(): SetlistDao
    abstract fun userDao(): UserDao
    abstract fun availabilityDao(): AvailabilityDao
    abstract fun setlistAssignmentDao(): SetlistAssignmentDao
    abstract fun syncMetadataDao(): SyncMetadataDao
}
