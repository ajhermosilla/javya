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
import java.time.LocalDate
import javax.inject.Inject

/**
 * Instrumented tests for SetlistDao.
 *
 * Tests CRUD operations for setlists and setlist-song associations.
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class SetlistDaoTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var database: JavyaDatabase

    private lateinit var setlistDao: SetlistDao
    private lateinit var songDao: SongDao

    @Before
    fun setup() {
        hiltRule.inject()
        setlistDao = database.setlistDao()
        songDao = database.songDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    // ==================== Insert Tests ====================

    @Test
    fun insertSetlist_insertsSuccessfully() = runTest {
        val setlist = TestData.createSetlistEntity()

        setlistDao.insert(setlist)

        val result = setlistDao.getSetlistByIdOnce(setlist.id)
        assertThat(result).isNotNull()
        assertThat(result!!.id).isEqualTo(setlist.id)
        assertThat(result.name).isEqualTo(setlist.name)
    }

    @Test
    fun insertAll_insertsMultipleSetlists() = runTest {
        val setlists = listOf(
            TestData.createSetlistEntity(id = "1", name = "Setlist 1"),
            TestData.createSetlistEntity(id = "2", name = "Setlist 2"),
            TestData.createSetlistEntity(id = "3", name = "Setlist 3")
        )

        setlistDao.insertAll(setlists)

        setlistDao.getAllSetlists().test {
            val result = awaitItem()
            assertThat(result).hasSize(3)
            cancelAndConsumeRemainingEvents()
        }
    }

    // ==================== Query Tests ====================

    @Test
    fun getAllSetlists_excludesDeleted() = runTest {
        val setlists = listOf(
            TestData.createSetlistEntity(id = "1"),
            TestData.createSetlistEntity(id = "2", syncStatus = SyncStatus.PENDING_DELETE)
        )
        setlistDao.insertAll(setlists)

        setlistDao.getAllSetlists().test {
            val result = awaitItem()
            assertThat(result).hasSize(1)
            assertThat(result[0].id).isEqualTo("1")
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun getSetlistById_returnsSetlist() = runTest {
        val setlist = TestData.createSetlistEntity(id = "test-id")
        setlistDao.insert(setlist)

        setlistDao.getSetlistById("test-id").test {
            val result = awaitItem()
            assertThat(result).isNotNull()
            assertThat(result!!.id).isEqualTo("test-id")
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun searchSetlists_byName() = runTest {
        val setlists = listOf(
            TestData.createSetlistEntity(id = "1", name = "Sunday Morning"),
            TestData.createSetlistEntity(id = "2", name = "Wednesday Night"),
            TestData.createSetlistEntity(id = "3", name = "Sunday Evening")
        )
        setlistDao.insertAll(setlists)

        setlistDao.searchSetlists("Sunday").test {
            val result = awaitItem()
            assertThat(result).hasSize(2)
            assertThat(result.map { it.name }).containsExactly("Sunday Morning", "Sunday Evening")
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun filterSetlists_byEventType() = runTest {
        val setlists = listOf(
            TestData.createSetlistEntity(id = "1", eventType = "sunday"),
            TestData.createSetlistEntity(id = "2", eventType = "wednesday"),
            TestData.createSetlistEntity(id = "3", eventType = "sunday")
        )
        setlistDao.insertAll(setlists)

        setlistDao.filterSetlists("sunday").test {
            val result = awaitItem()
            assertThat(result).hasSize(2)
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun filterSetlists_withNullEventType_returnsAll() = runTest {
        val setlists = listOf(
            TestData.createSetlistEntity(id = "1", eventType = "sunday"),
            TestData.createSetlistEntity(id = "2", eventType = "wednesday")
        )
        setlistDao.insertAll(setlists)

        setlistDao.filterSetlists(null).test {
            val result = awaitItem()
            assertThat(result).hasSize(2)
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun getSetlistsByDateRange_returnsSetlistsInRange() = runTest {
        val today = LocalDate.now()
        val setlists = listOf(
            TestData.createSetlistEntity(id = "1", serviceDate = today.minusDays(10).toString()),
            TestData.createSetlistEntity(id = "2", serviceDate = today.toString()),
            TestData.createSetlistEntity(id = "3", serviceDate = today.plusDays(10).toString()),
            TestData.createSetlistEntity(id = "4", serviceDate = today.plusDays(30).toString())
        )
        setlistDao.insertAll(setlists)

        val startDate = today.minusDays(5).toString()
        val endDate = today.plusDays(15).toString()

        setlistDao.getSetlistsByDateRange(startDate, endDate).test {
            val result = awaitItem()
            assertThat(result).hasSize(2)
            assertThat(result.map { it.id }).containsExactly("2", "3")
            cancelAndConsumeRemainingEvents()
        }
    }

    // ==================== Update Tests ====================

    @Test
    fun update_modifiesSetlist() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1", name = "Original")
        setlistDao.insert(setlist)

        val updated = setlist.copy(name = "Updated", description = "New description")
        setlistDao.update(updated)

        val result = setlistDao.getSetlistByIdOnce("setlist-1")
        assertThat(result!!.name).isEqualTo("Updated")
        assertThat(result.description).isEqualTo("New description")
    }

    @Test
    fun updateSyncStatus_modifiesOnlyStatus() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1", syncStatus = SyncStatus.SYNCED)
        setlistDao.insert(setlist)

        setlistDao.updateSyncStatus("setlist-1", SyncStatus.PENDING_UPDATE)

        val result = setlistDao.getSetlistByIdOnce("setlist-1")
        assertThat(result!!.syncStatus).isEqualTo(SyncStatus.PENDING_UPDATE)
    }

    // ==================== Delete Tests ====================

    @Test
    fun deleteById_removesSetlist() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1")
        setlistDao.insert(setlist)

        setlistDao.deleteById("setlist-1")

        val result = setlistDao.getSetlistByIdOnce("setlist-1")
        assertThat(result).isNull()
    }

    // ==================== Setlist Songs Tests ====================

    @Test
    fun insertSetlistSong_insertsSuccessfully() = runTest {
        // First insert setlist and song (foreign key constraint)
        val setlist = TestData.createSetlistEntity(id = "setlist-1")
        val song = TestData.createSongEntity(id = "song-1")
        setlistDao.insert(setlist)
        songDao.insert(song)

        val setlistSong = TestData.createSetlistSongEntity(
            id = "ss-1",
            setlistId = "setlist-1",
            songId = "song-1",
            position = 0
        )
        setlistDao.insertSetlistSong(setlistSong)

        val result = setlistDao.getSetlistSongsOnce("setlist-1")
        assertThat(result).hasSize(1)
        assertThat(result[0].songId).isEqualTo("song-1")
    }

    @Test
    fun getSetlistSongs_orderedByPosition() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1")
        val songs = listOf(
            TestData.createSongEntity(id = "song-1"),
            TestData.createSongEntity(id = "song-2"),
            TestData.createSongEntity(id = "song-3")
        )
        setlistDao.insert(setlist)
        songDao.insertAll(songs)

        val setlistSongs = listOf(
            TestData.createSetlistSongEntity(id = "ss-1", setlistId = "setlist-1", songId = "song-3", position = 2),
            TestData.createSetlistSongEntity(id = "ss-2", setlistId = "setlist-1", songId = "song-1", position = 0),
            TestData.createSetlistSongEntity(id = "ss-3", setlistId = "setlist-1", songId = "song-2", position = 1)
        )
        setlistDao.insertSetlistSongs(setlistSongs)

        setlistDao.getSetlistSongs("setlist-1").test {
            val result = awaitItem()
            assertThat(result).hasSize(3)
            assertThat(result.map { it.songId }).containsExactly("song-1", "song-2", "song-3").inOrder()
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun deleteSetlistSongs_removesAllForSetlist() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1")
        val songs = listOf(
            TestData.createSongEntity(id = "song-1"),
            TestData.createSongEntity(id = "song-2")
        )
        setlistDao.insert(setlist)
        songDao.insertAll(songs)

        val setlistSongs = listOf(
            TestData.createSetlistSongEntity(id = "ss-1", setlistId = "setlist-1", songId = "song-1", position = 0),
            TestData.createSetlistSongEntity(id = "ss-2", setlistId = "setlist-1", songId = "song-2", position = 1)
        )
        setlistDao.insertSetlistSongs(setlistSongs)

        setlistDao.deleteSetlistSongs("setlist-1")

        val result = setlistDao.getSetlistSongsOnce("setlist-1")
        assertThat(result).isEmpty()
    }

    @Test
    fun replaceSetlistSongs_replacesAll() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1")
        val songs = listOf(
            TestData.createSongEntity(id = "song-1"),
            TestData.createSongEntity(id = "song-2"),
            TestData.createSongEntity(id = "song-3")
        )
        setlistDao.insert(setlist)
        songDao.insertAll(songs)

        // Initial songs
        val initialSongs = listOf(
            TestData.createSetlistSongEntity(id = "ss-1", setlistId = "setlist-1", songId = "song-1", position = 0),
            TestData.createSetlistSongEntity(id = "ss-2", setlistId = "setlist-1", songId = "song-2", position = 1)
        )
        setlistDao.insertSetlistSongs(initialSongs)

        // Replace with new songs
        val newSongs = listOf(
            TestData.createSetlistSongEntity(id = "ss-3", setlistId = "setlist-1", songId = "song-3", position = 0),
            TestData.createSetlistSongEntity(id = "ss-4", setlistId = "setlist-1", songId = "song-1", position = 1)
        )
        setlistDao.replaceSetlistSongs("setlist-1", newSongs)

        val result = setlistDao.getSetlistSongsOnce("setlist-1")
        assertThat(result).hasSize(2)
        assertThat(result.map { it.songId }).containsExactly("song-3", "song-1").inOrder()
    }

    @Test
    fun updateSetlistSongPosition_modifiesPosition() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1")
        val song = TestData.createSongEntity(id = "song-1")
        setlistDao.insert(setlist)
        songDao.insert(song)

        val setlistSong = TestData.createSetlistSongEntity(
            id = "ss-1",
            setlistId = "setlist-1",
            songId = "song-1",
            position = 0
        )
        setlistDao.insertSetlistSong(setlistSong)

        setlistDao.updateSetlistSongPosition("ss-1", 5)

        val result = setlistDao.getSetlistSongsOnce("setlist-1")
        assertThat(result[0].position).isEqualTo(5)
    }

    // ==================== Sync Tests ====================

    @Test
    fun getPendingChanges_returnsUnsynced() = runTest {
        val setlists = listOf(
            TestData.createSetlistEntity(id = "1", syncStatus = SyncStatus.SYNCED),
            TestData.createSetlistEntity(id = "2", syncStatus = SyncStatus.PENDING_CREATE),
            TestData.createSetlistEntity(id = "3", syncStatus = SyncStatus.PENDING_UPDATE)
        )
        setlistDao.insertAll(setlists)

        val pending = setlistDao.getPendingChanges()

        assertThat(pending).hasSize(2)
        assertThat(pending.map { it.id }).containsExactly("2", "3")
    }

    // ==================== Cascade Delete Tests ====================

    @Test
    fun deleteSetlist_cascadesDeleteToSetlistSongs() = runTest {
        val setlist = TestData.createSetlistEntity(id = "setlist-1")
        val song = TestData.createSongEntity(id = "song-1")
        setlistDao.insert(setlist)
        songDao.insert(song)

        val setlistSong = TestData.createSetlistSongEntity(
            id = "ss-1",
            setlistId = "setlist-1",
            songId = "song-1",
            position = 0
        )
        setlistDao.insertSetlistSong(setlistSong)

        // Delete the setlist
        setlistDao.deleteById("setlist-1")

        // Setlist songs should be deleted due to cascade
        val result = setlistDao.getSetlistSongsOnce("setlist-1")
        assertThat(result).isEmpty()
    }
}
