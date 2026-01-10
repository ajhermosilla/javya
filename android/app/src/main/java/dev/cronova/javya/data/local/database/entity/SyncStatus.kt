package dev.cronova.javya.data.local.database.entity

/**
 * Sync status for offline-first operations.
 */
enum class SyncStatus {
    SYNCED,           // Data matches server
    PENDING_CREATE,   // Created offline, needs upload
    PENDING_UPDATE,   // Modified offline, needs upload
    PENDING_DELETE    // Deleted offline, needs server deletion
}
