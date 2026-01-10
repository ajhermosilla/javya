package dev.cronova.javya.data.remote.dto.scheduling

import com.google.gson.annotations.SerializedName

data class CalendarSetlistResponse(
    val id: String,
    val name: String,
    @SerializedName("service_date")
    val serviceDate: String?,
    @SerializedName("event_type")
    val eventType: String?,
    @SerializedName("song_count")
    val songCount: Int,
    val assignments: List<SetlistAssignmentResponse>
)

data class MyAssignmentResponse(
    val id: String,
    @SerializedName("service_role")
    val serviceRole: String,
    val notes: String?,
    val confirmed: Boolean,
    @SerializedName("setlist_id")
    val setlistId: String,
    @SerializedName("setlist_name")
    val setlistName: String,
    @SerializedName("service_date")
    val serviceDate: String?,
    @SerializedName("event_type")
    val eventType: String?
)

data class TeamAvailabilityResponse(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("user_name")
    val userName: String,
    @SerializedName("user_email")
    val userEmail: String,
    @SerializedName("user_role")
    val userRole: String,
    val status: String?
)

data class SetlistAssignmentResponse(
    val id: String,
    @SerializedName("setlist_id")
    val setlistId: String,
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("service_role")
    val serviceRole: String,
    val notes: String?,
    val confirmed: Boolean,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String,
    @SerializedName("user_name")
    val userName: String,
    @SerializedName("user_email")
    val userEmail: String,
    @SerializedName("user_role")
    val userRole: String,
    @SerializedName("availability_status")
    val availabilityStatus: String?
)

data class SetlistAssignmentCreateRequest(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("service_role")
    val serviceRole: String,
    val notes: String? = null
)

data class SetlistAssignmentUpdateRequest(
    @SerializedName("service_role")
    val serviceRole: String? = null,
    val notes: String? = null
)
