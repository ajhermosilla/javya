package dev.cronova.javya.util

import android.content.Context
import androidx.room.Room
import dagger.Module
import dagger.Provides
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import dagger.hilt.testing.TestInstallIn
import dev.cronova.javya.data.local.database.JavyaDatabase
import dev.cronova.javya.di.DatabaseModule
import javax.inject.Singleton

/**
 * Test module that replaces DatabaseModule with an in-memory database.
 */
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [DatabaseModule::class]
)
object TestDatabaseModule {

    @Provides
    @Singleton
    fun provideTestDatabase(
        @ApplicationContext context: Context
    ): JavyaDatabase {
        return Room.inMemoryDatabaseBuilder(
            context,
            JavyaDatabase::class.java
        )
            .allowMainThreadQueries() // For testing only
            .build()
    }

    @Provides
    fun provideSongDao(database: JavyaDatabase) = database.songDao()

    @Provides
    fun provideSetlistDao(database: JavyaDatabase) = database.setlistDao()

    @Provides
    fun provideSetlistSongDao(database: JavyaDatabase) = database.setlistSongDao()

    @Provides
    fun provideUserDao(database: JavyaDatabase) = database.userDao()

    @Provides
    fun provideAvailabilityDao(database: JavyaDatabase) = database.availabilityDao()

    @Provides
    fun provideSyncMetadataDao(database: JavyaDatabase) = database.syncMetadataDao()
}
