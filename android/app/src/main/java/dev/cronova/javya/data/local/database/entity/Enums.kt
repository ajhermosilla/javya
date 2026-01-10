package dev.cronova.javya.data.local.database.entity

/**
 * Musical keys following the Circle of Fifths.
 */
enum class MusicalKey(val displayName: String) {
    // Natural key
    C("C"),

    // Sharp keys (Circle of Fifths clockwise)
    G("G"),
    D("D"),
    A("A"),
    E("E"),
    B("B"),
    F_SHARP("F#"),
    C_SHARP("C#"),

    // Flat keys (Circle of Fifths counter-clockwise)
    F("F"),
    B_FLAT("Bb"),
    E_FLAT("Eb"),
    A_FLAT("Ab"),
    D_FLAT("Db"),
    G_FLAT("Gb"),

    // Enharmonic equivalents (for backward compatibility)
    D_SHARP("D#"),
    G_SHARP("G#"),
    A_SHARP("A#");

    companion object {
        fun fromString(value: String?): MusicalKey? {
            if (value == null) return null
            return entries.find { it.displayName == value || it.name == value }
        }
    }
}

/**
 * Song moods for categorization.
 */
enum class Mood(val displayName: String) {
    JOYFUL("Joyful"),
    REFLECTIVE("Reflective"),
    TRIUMPHANT("Triumphant"),
    INTIMATE("Intimate"),
    PEACEFUL("Peaceful"),
    ENERGETIC("Energetic"),
    HOPEFUL("Hopeful"),
    SOLEMN("Solemn"),
    CELEBRATORY("Celebratory");

    companion object {
        fun fromString(value: String?): Mood? {
            if (value == null) return null
            return entries.find { it.displayName == value || it.name == value }
        }
    }
}

/**
 * Song themes for categorization.
 */
enum class Theme(val displayName: String) {
    WORSHIP("Worship"),
    COMMUNION("Communion"),
    OFFERING("Offering"),
    OPENING("Opening"),
    CLOSING("Closing"),
    PRAYER("Prayer"),
    DECLARATION("Declaration"),
    THANKSGIVING("Thanksgiving"),
    FAITH("Faith"),
    GRACE("Grace"),
    SALVATION("Salvation"),
    BAPTISM("Baptism"),
    CHRISTMAS("Christmas"),
    HOLY_WEEK("Holy Week");

    companion object {
        fun fromString(value: String?): Theme? {
            if (value == null) return null
            return entries.find { it.displayName == value || it.name == value }
        }
    }
}

/**
 * Event types for setlists.
 */
enum class EventType(val displayName: String) {
    SUNDAY("Sunday"),
    WEDNESDAY("Wednesday"),
    YOUTH("Youth"),
    SPECIAL("Special"),
    RETREAT("Retreat"),
    OTHER("Other");

    companion object {
        fun fromString(value: String?): EventType? {
            if (value == null) return null
            return entries.find { it.displayName == value || it.name == value }
        }
    }
}

/**
 * User roles for authorization.
 */
enum class UserRole(val apiValue: String) {
    ADMIN("admin"),
    LEADER("leader"),
    MEMBER("member");

    companion object {
        fun fromString(value: String?): UserRole? {
            if (value == null) return null
            return entries.find { it.apiValue == value || it.name == value }
        }
    }
}

/**
 * Availability status for a specific date.
 */
enum class AvailabilityStatus(val apiValue: String) {
    AVAILABLE("available"),
    UNAVAILABLE("unavailable"),
    MAYBE("maybe");

    companion object {
        fun fromString(value: String?): AvailabilityStatus? {
            if (value == null) return null
            return entries.find { it.apiValue == value || it.name == value }
        }
    }
}

/**
 * Recurrence pattern types for availability.
 */
enum class PatternType(val apiValue: String) {
    WEEKLY("weekly"),
    BIWEEKLY("biweekly"),
    MONTHLY("monthly");

    companion object {
        fun fromString(value: String?): PatternType? {
            if (value == null) return null
            return entries.find { it.apiValue == value || it.name == value }
        }
    }
}

/**
 * Roles that team members can fulfill in a service.
 */
enum class ServiceRole(val apiValue: String) {
    WORSHIP_LEADER("worship_leader"),
    VOCALIST("vocalist"),
    GUITARIST("guitarist"),
    BASSIST("bassist"),
    DRUMMER("drummer"),
    KEYS("keys"),
    SOUND("sound"),
    PROJECTION("projection"),
    OTHER("other");

    companion object {
        fun fromString(value: String?): ServiceRole? {
            if (value == null) return null
            return entries.find { it.apiValue == value || it.name == value }
        }
    }
}
