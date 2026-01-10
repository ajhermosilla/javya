package dev.cronova.javya

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.Event
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.QueueMusic
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.outlined.CalendarMonth
import androidx.compose.material.icons.outlined.Event
import androidx.compose.material.icons.outlined.MusicNote
import androidx.compose.material.icons.outlined.QueueMusic
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import dagger.hilt.android.AndroidEntryPoint
import dev.cronova.javya.data.local.datastore.AuthDataStore
import dev.cronova.javya.ui.navigation.JavyaNavGraph
import dev.cronova.javya.ui.navigation.Routes
import dev.cronova.javya.ui.theme.JavyaTheme
import javax.inject.Inject

/**
 * Bottom navigation item definition.
 */
data class BottomNavItem(
    val route: String,
    val labelResId: Int,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
)

val bottomNavItems = listOf(
    BottomNavItem(
        route = Routes.SONGS,
        labelResId = R.string.nav_songs,
        selectedIcon = Icons.Filled.MusicNote,
        unselectedIcon = Icons.Outlined.MusicNote
    ),
    BottomNavItem(
        route = Routes.SETLISTS,
        labelResId = R.string.nav_setlists,
        selectedIcon = Icons.Filled.QueueMusic,
        unselectedIcon = Icons.Outlined.QueueMusic
    ),
    BottomNavItem(
        route = Routes.AVAILABILITY,
        labelResId = R.string.nav_availability,
        selectedIcon = Icons.Filled.CalendarMonth,
        unselectedIcon = Icons.Outlined.CalendarMonth
    ),
    BottomNavItem(
        route = Routes.SCHEDULING,
        labelResId = R.string.nav_scheduling,
        selectedIcon = Icons.Filled.Event,
        unselectedIcon = Icons.Outlined.Event
    ),
    BottomNavItem(
        route = Routes.SETTINGS,
        labelResId = R.string.nav_settings,
        selectedIcon = Icons.Filled.Settings,
        unselectedIcon = Icons.Outlined.Settings
    )
)

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var authDataStore: AuthDataStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            JavyaTheme {
                val isLoggedIn by authDataStore.isLoggedIn.collectAsState(initial = false)
                JavyaApp(isLoggedIn = isLoggedIn)
            }
        }
    }
}

@Composable
fun JavyaApp(isLoggedIn: Boolean) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    // Determine if we should show the bottom navigation
    val showBottomNav = isLoggedIn && currentDestination?.route in listOf(
        Routes.SONGS,
        Routes.SETLISTS,
        Routes.AVAILABILITY,
        Routes.SCHEDULING,
        Routes.SETTINGS
    )

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        bottomBar = {
            if (showBottomNav) {
                NavigationBar {
                    bottomNavItems.forEach { item ->
                        val selected = currentDestination?.hierarchy?.any {
                            it.route == item.route
                        } == true

                        NavigationBarItem(
                            icon = {
                                Icon(
                                    imageVector = if (selected) {
                                        item.selectedIcon
                                    } else {
                                        item.unselectedIcon
                                    },
                                    contentDescription = stringResource(item.labelResId)
                                )
                            },
                            label = { Text(stringResource(item.labelResId)) },
                            selected = selected,
                            onClick = {
                                navController.navigate(item.route) {
                                    // Pop up to the start destination of the graph to
                                    // avoid building up a large stack of destinations
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    // Avoid multiple copies of the same destination
                                    launchSingleTop = true
                                    // Restore state when reselecting a previously selected item
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        JavyaNavGraph(
            navController = navController,
            isLoggedIn = isLoggedIn,
            modifier = Modifier.padding(innerPadding)
        )
    }
}
