package dev.cronova.javya.data.local.database.converter

import androidx.room.TypeConverter
import dev.cronova.javya.data.local.database.entity.SyncStatus

/**
 * Room type converters for complex types.
 */
class Converters {

    @TypeConverter
    fun fromSyncStatus(status: SyncStatus): String = status.name

    @TypeConverter
    fun toSyncStatus(value: String): SyncStatus = SyncStatus.valueOf(value)
}
