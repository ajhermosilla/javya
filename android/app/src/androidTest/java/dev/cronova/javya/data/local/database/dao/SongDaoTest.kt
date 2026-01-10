package dev.cronova.javya.data.local.database.dao

import androidx.test.ext.junit.runners.AndroidJUnit4
import app.cash.turbine.test
import com.google.common.truth.Truth.assertThat
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dev.cronova.javya.data.local.database.JavyaDatabase
import dev.cronova.javya.data.local.database.entity.SyncStatus
import dev.cronova.javya.util.TestData
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import javax.inject.Inject

/**
 * Instrumented tests for SongDao.
 *
 * Tests CRUD operations and queries against an in-memory database.
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class SongDaoTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var database: JavyaDatabase

    private lateinit var songDao: SongDao

    @Before
    fun setup() {
        hiltRule.inject()
        songDao = database.songDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    // ==================== Insert Tests ====================

    @Test
    fun insertSong_insertsSuccessfully() = runTest {
        val song = TestData.createSongEntity()

        songDao.insert(song)

        val result = songDao.getSongByIdOnce(song.id)
        assertThat(result).isNotNull()
        assertThat(result!!.id).isEqualTo(song.id)
        assertThat(result.name).isEqualTo(song.name)
    }

    @Test
    fun insertAll_insertsMultipleSongs() = runTest {
        val songs = TestData.createSongList(5)

        songDao.insertAll(songs)

        val count = songDao.getSongCount()
        assertThat(count).isEqualTo(5)
    }

    @Test
    fun insert_withSameId_replaces() = runTest {
        val song = TestData.createSongEntity(id = "song-1", name = "Original")
        songDao.insert(song)

        val updated = song.copy(name = "Updated")
        songDao.insert(updated)

        val result = songDao.getSongByIdOnce("song-1")
        assertThat(result!!.name).isEqualTo("Updated")

        val count = songDao.getSongCount()
        assertThat(count).isEqualTo(1)
    }

    // ==================== Query Tests ====================

    @Test
    fun getAllSongs_returnsAllNonDeleted() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", name = "Song A"),
            TestData.createSongEntity(id = "2", name = "Song B"),
            TestData.createSongEntity(id = "3", name = "Song C", syncStatus = SyncStatus.PENDING_DELETE)
        )
        songDao.insertAll(songs)

        songDao.getAllSongs().test {
            val result = awaitItem()
            assertThat(result).hasSize(2)
            assertThat(result.map { it.id }).containsExactly("1", "2")
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun getAllSongs_orderedByName() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", name = "Charlie"),
            TestData.createSongEntity(id = "2", name = "Alpha"),
            TestData.createSongEntity(id = "3", name = "Bravo")
        )
        songDao.insertAll(songs)

        songDao.getAllSongs().test {
            val result = awaitItem()
            assertThat(result.map { it.name }).containsExactly("Alpha", "Bravo", "Charlie").inOrder()
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun getSongById_returnsSong() = runTest {
        val song = TestData.createSongEntity(id = "test-id")
        songDao.insert(song)

        songDao.getSongById("test-id").test {
            val result = awaitItem()
            assertThat(result).isNotNull()
            assertThat(result!!.id).isEqualTo("test-id")
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun getSongById_returnsNullForNonexistent() = runTest {
        songDao.getSongById("nonexistent").test {
            val result = awaitItem()
            assertThat(result).isNull()
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun getSongByIdOnce_returnsSong() = runTest {
        val song = TestData.createSongEntity(id = "test-id")
        songDao.insert(song)

        val result = songDao.getSongByIdOnce("test-id")
        assertThat(result).isNotNull()
        assertThat(result!!.id).isEqualTo("test-id")
    }

    // ==================== Search Tests ====================

    @Test
    fun searchSongs_byName() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", name = "Amazing Grace"),
            TestData.createSongEntity(id = "2", name = "How Great Is Our God"),
            TestData.createSongEntity(id = "3", name = "Amazing Love")
        )
        songDao.insertAll(songs)

        songDao.searchSongs("Amazing").test {
            val result = awaitItem()
            assertThat(result).hasSize(2)
            assertThat(result.map { it.name }).containsExactly("Amazing Grace", "Amazing Love")
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun searchSongs_byArtist() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", name = "Song A", artist = "John Newton"),
            TestData.createSongEntity(id = "2", name = "Song B", artist = "Chris Tomlin"),
            TestData.createSongEntity(id = "3", name = "Song C", artist = "John Smith")
        )
        songDao.insertAll(songs)

        songDao.searchSongs("John").test {
            val result = awaitItem()
            assertThat(result).hasSize(2)
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun searchSongs_caseInsensitive() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", name = "Amazing Grace")
        )
        songDao.insertAll(songs)

        songDao.searchSongs("amazing").test {
            val result = awaitItem()
            assertThat(result).hasSize(1)
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun searchSongs_excludesDeleted() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", name = "Amazing Grace"),
            TestData.createSongEntity(id = "2", name = "Amazing Love", syncStatus = SyncStatus.PENDING_DELETE)
        )
        songDao.insertAll(songs)

        songDao.searchSongs("Amazing").test {
            val result = awaitItem()
            assertThat(result).hasSize(1)
            assertThat(result[0].name).isEqualTo("Amazing Grace")
            cancelAndConsumeRemainingEvents()
        }
    }

    // ==================== Pagination Tests ====================

    @Test
    fun getSongsPaginated_returnsCorrectPage() = runTest {
        val songs = (1..10).map { i ->
            TestData.createSongEntity(id = "$i", name = "Song ${String.format("%02d", i)}")
        }
        songDao.insertAll(songs)

        val page1 = songDao.getSongsPaginated(limit = 3, offset = 0)
        assertThat(page1).hasSize(3)
        assertThat(page1.map { it.name }).containsExactly("Song 01", "Song 02", "Song 03").inOrder()

        val page2 = songDao.getSongsPaginated(limit = 3, offset = 3)
        assertThat(page2).hasSize(3)
        assertThat(page2.map { it.name }).containsExactly("Song 04", "Song 05", "Song 06").inOrder()
    }

    @Test
    fun getSongCount_returnsCorrectCount() = runTest {
        val songs = TestData.createSongList(7)
        songDao.insertAll(songs)

        val count = songDao.getSongCount()
        assertThat(count).isEqualTo(7)
    }

    @Test
    fun getSongCount_excludesDeleted() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1"),
            TestData.createSongEntity(id = "2"),
            TestData.createSongEntity(id = "3", syncStatus = SyncStatus.PENDING_DELETE)
        )
        songDao.insertAll(songs)

        val count = songDao.getSongCount()
        assertThat(count).isEqualTo(2)
    }

    // ==================== Update Tests ====================

    @Test
    fun update_modifiesSong() = runTest {
        val song = TestData.createSongEntity(id = "song-1", name = "Original")
        songDao.insert(song)

        val updated = song.copy(name = "Updated", artist = "New Artist")
        songDao.update(updated)

        val result = songDao.getSongByIdOnce("song-1")
        assertThat(result!!.name).isEqualTo("Updated")
        assertThat(result.artist).isEqualTo("New Artist")
    }

    @Test
    fun updateSyncStatus_modifiesOnlyStatus() = runTest {
        val song = TestData.createSongEntity(id = "song-1", syncStatus = SyncStatus.SYNCED)
        songDao.insert(song)

        songDao.updateSyncStatus("song-1", SyncStatus.PENDING_UPDATE)

        val result = songDao.getSongByIdOnce("song-1")
        assertThat(result!!.syncStatus).isEqualTo(SyncStatus.PENDING_UPDATE)
    }

    // ==================== Delete Tests ====================

    @Test
    fun deleteById_removesSong() = runTest {
        val song = TestData.createSongEntity(id = "song-1")
        songDao.insert(song)

        songDao.deleteById("song-1")

        val result = songDao.getSongByIdOnce("song-1")
        assertThat(result).isNull()
    }

    @Test
    fun deletePendingDeletes_removesOnlyPendingDeleted() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", syncStatus = SyncStatus.SYNCED),
            TestData.createSongEntity(id = "2", syncStatus = SyncStatus.PENDING_UPDATE),
            TestData.createSongEntity(id = "3", syncStatus = SyncStatus.PENDING_DELETE)
        )
        songDao.insertAll(songs)

        songDao.deletePendingDeletes()

        val synced = songDao.getSongByIdOnce("1")
        val pendingUpdate = songDao.getSongByIdOnce("2")
        val pendingDelete = songDao.getSongByIdOnce("3")

        assertThat(synced).isNotNull()
        assertThat(pendingUpdate).isNotNull()
        assertThat(pendingDelete).isNull()
    }

    // ==================== Sync Tests ====================

    @Test
    fun getPendingChanges_returnsUnsynced() = runTest {
        val songs = listOf(
            TestData.createSongEntity(id = "1", syncStatus = SyncStatus.SYNCED),
            TestData.createSongEntity(id = "2", syncStatus = SyncStatus.PENDING_CREATE),
            TestData.createSongEntity(id = "3", syncStatus = SyncStatus.PENDING_UPDATE),
            TestData.createSongEntity(id = "4", syncStatus = SyncStatus.PENDING_DELETE)
        )
        songDao.insertAll(songs)

        val pending = songDao.getPendingChanges()

        assertThat(pending).hasSize(3)
        assertThat(pending.map { it.id }).containsExactly("2", "3", "4")
    }

    // ==================== Flow Reactivity Tests ====================

    @Test
    fun getAllSongs_emitsOnInsert() = runTest {
        songDao.getAllSongs().test {
            // Initial empty state
            assertThat(awaitItem()).isEmpty()

            // Insert a song
            val song = TestData.createSongEntity(id = "1")
            songDao.insert(song)

            // Should emit updated list
            val result = awaitItem()
            assertThat(result).hasSize(1)
            assertThat(result[0].id).isEqualTo("1")

            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun getAllSongs_emitsOnDelete() = runTest {
        val song = TestData.createSongEntity(id = "1")
        songDao.insert(song)

        songDao.getAllSongs().test {
            // Initial state with one song
            assertThat(awaitItem()).hasSize(1)

            // Delete the song
            songDao.deleteById("1")

            // Should emit empty list
            assertThat(awaitItem()).isEmpty()

            cancelAndConsumeRemainingEvents()
        }
    }
}
