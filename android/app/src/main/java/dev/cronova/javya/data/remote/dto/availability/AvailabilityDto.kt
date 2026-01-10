package dev.cronova.javya.data.remote.dto.availability

import com.google.gson.annotations.SerializedName

data class AvailabilityResponse(
    val id: String,
    @SerializedName("user_id")
    val userId: String,
    val date: String,
    val status: String,
    val note: String?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class AvailabilityCreateRequest(
    val date: String,
    val status: String,
    val note: String? = null
)

data class BulkAvailabilityRequest(
    val entries: List<AvailabilityCreateRequest>
)

data class AvailabilityPatternResponse(
    val id: String,
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("pattern_type")
    val patternType: String,
    @SerializedName("day_of_week")
    val dayOfWeek: Int,
    val status: String,
    @SerializedName("start_date")
    val startDate: String?,
    @SerializedName("end_date")
    val endDate: String?,
    @SerializedName("is_active")
    val isActive: Boolean,
    val note: String?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class AvailabilityPatternCreateRequest(
    @SerializedName("pattern_type")
    val patternType: String,
    @SerializedName("day_of_week")
    val dayOfWeek: Int,
    val status: String,
    @SerializedName("start_date")
    val startDate: String? = null,
    @SerializedName("end_date")
    val endDate: String? = null,
    val note: String? = null
)

data class AvailabilityPatternUpdateRequest(
    @SerializedName("pattern_type")
    val patternType: String? = null,
    @SerializedName("day_of_week")
    val dayOfWeek: Int? = null,
    val status: String? = null,
    @SerializedName("start_date")
    val startDate: String? = null,
    @SerializedName("end_date")
    val endDate: String? = null,
    @SerializedName("is_active")
    val isActive: Boolean? = null,
    val note: String? = null
)
