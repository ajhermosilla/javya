package dev.cronova.javya.di

import android.content.Context
import androidx.room.Room
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import dev.cronova.javya.data.local.database.JavyaDatabase
import dev.cronova.javya.data.local.database.dao.AvailabilityDao
import dev.cronova.javya.data.local.database.dao.SetlistAssignmentDao
import dev.cronova.javya.data.local.database.dao.SetlistDao
import dev.cronova.javya.data.local.database.dao.SongDao
import dev.cronova.javya.data.local.database.dao.SyncMetadataDao
import dev.cronova.javya.data.local.database.dao.UserDao
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): JavyaDatabase = Room.databaseBuilder(
        context,
        JavyaDatabase::class.java,
        "javya_database"
    )
        .fallbackToDestructiveMigration()
        .build()

    @Provides
    fun provideSongDao(database: JavyaDatabase): SongDao = database.songDao()

    @Provides
    fun provideSetlistDao(database: JavyaDatabase): SetlistDao = database.setlistDao()

    @Provides
    fun provideUserDao(database: JavyaDatabase): UserDao = database.userDao()

    @Provides
    fun provideAvailabilityDao(database: JavyaDatabase): AvailabilityDao = database.availabilityDao()

    @Provides
    fun provideSetlistAssignmentDao(database: JavyaDatabase): SetlistAssignmentDao = database.setlistAssignmentDao()

    @Provides
    fun provideSyncMetadataDao(database: JavyaDatabase): SyncMetadataDao = database.syncMetadataDao()
}
