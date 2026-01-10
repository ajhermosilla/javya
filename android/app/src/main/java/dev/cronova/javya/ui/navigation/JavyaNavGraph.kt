package dev.cronova.javya.ui.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import dev.cronova.javya.ui.auth.LoginScreen

/**
 * Navigation routes for the app.
 */
object Routes {
    const val LOGIN = "login"
    const val SONGS = "songs"
    const val SONG_DETAIL = "songs/{songId}"
    const val SONG_FORM = "songs/form"
    const val SONG_EDIT = "songs/{songId}/edit"
    const val SETLISTS = "setlists"
    const val SETLIST_DETAIL = "setlists/{setlistId}"
    const val SETLIST_FORM = "setlists/form"
    const val SETLIST_EDIT = "setlists/{setlistId}/edit"
    const val SETLIST_SERVICE = "setlists/{setlistId}/service"
    const val AVAILABILITY = "availability"
    const val SCHEDULING = "scheduling"
    const val SETTINGS = "settings"

    fun songDetail(songId: String) = "songs/$songId"
    fun songEdit(songId: String) = "songs/$songId/edit"
    fun setlistDetail(setlistId: String) = "setlists/$setlistId"
    fun setlistEdit(setlistId: String) = "setlists/$setlistId/edit"
    fun setlistService(setlistId: String) = "setlists/$setlistId/service"
}

/**
 * Main navigation graph for the app.
 */
@Composable
fun JavyaNavGraph(
    navController: NavHostController,
    isLoggedIn: Boolean,
    modifier: Modifier = Modifier
) {
    val startDestination = if (isLoggedIn) Routes.SONGS else Routes.LOGIN

    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier
    ) {
        // Auth
        composable(Routes.LOGIN) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Routes.SONGS) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }

        // Songs
        composable(Routes.SONGS) {
            // TODO: SongListScreen
            PlaceholderScreen(title = "Songs")
        }

        composable(Routes.SONG_DETAIL) { backStackEntry ->
            val songId = backStackEntry.arguments?.getString("songId") ?: return@composable
            // TODO: SongDetailScreen
            PlaceholderScreen(title = "Song: $songId")
        }

        composable(Routes.SONG_FORM) {
            // TODO: SongFormScreen (create)
            PlaceholderScreen(title = "New Song")
        }

        composable(Routes.SONG_EDIT) { backStackEntry ->
            val songId = backStackEntry.arguments?.getString("songId") ?: return@composable
            // TODO: SongFormScreen (edit)
            PlaceholderScreen(title = "Edit Song: $songId")
        }

        // Setlists
        composable(Routes.SETLISTS) {
            // TODO: SetlistListScreen
            PlaceholderScreen(title = "Setlists")
        }

        composable(Routes.SETLIST_DETAIL) { backStackEntry ->
            val setlistId = backStackEntry.arguments?.getString("setlistId") ?: return@composable
            // TODO: SetlistDetailScreen
            PlaceholderScreen(title = "Setlist: $setlistId")
        }

        composable(Routes.SETLIST_FORM) {
            // TODO: SetlistFormScreen (create)
            PlaceholderScreen(title = "New Setlist")
        }

        composable(Routes.SETLIST_EDIT) { backStackEntry ->
            val setlistId = backStackEntry.arguments?.getString("setlistId") ?: return@composable
            // TODO: SetlistEditorScreen
            PlaceholderScreen(title = "Edit Setlist: $setlistId")
        }

        composable(Routes.SETLIST_SERVICE) { backStackEntry ->
            val setlistId = backStackEntry.arguments?.getString("setlistId") ?: return@composable
            // TODO: WorshipServiceScreen
            PlaceholderScreen(title = "Service Mode: $setlistId")
        }

        // Availability
        composable(Routes.AVAILABILITY) {
            // TODO: AvailabilityScreen
            PlaceholderScreen(title = "Availability")
        }

        // Scheduling
        composable(Routes.SCHEDULING) {
            // TODO: SchedulingScreen
            PlaceholderScreen(title = "Scheduling")
        }

        // Settings
        composable(Routes.SETTINGS) {
            // TODO: SettingsScreen
            PlaceholderScreen(title = "Settings")
        }
    }
}

/**
 * Temporary placeholder screen for unimplemented routes.
 */
@Composable
private fun PlaceholderScreen(title: String) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.headlineMedium
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Coming soon...",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
