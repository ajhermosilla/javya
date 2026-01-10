package dev.cronova.javya.data.remote.dto.setlist

import com.google.gson.annotations.SerializedName
import dev.cronova.javya.data.remote.dto.song.SongResponse

data class SetlistResponse(
    val id: String,
    val name: String,
    val description: String?,
    @SerializedName("service_date")
    val serviceDate: String?,
    @SerializedName("event_type")
    val eventType: String?,
    @SerializedName("song_count")
    val songCount: Int,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class SetlistDetailResponse(
    val id: String,
    val name: String,
    val description: String?,
    @SerializedName("service_date")
    val serviceDate: String?,
    @SerializedName("event_type")
    val eventType: String?,
    @SerializedName("song_count")
    val songCount: Int,
    val songs: List<SetlistSongResponse>,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class SetlistSongResponse(
    val id: String,
    @SerializedName("song_id")
    val songId: String,
    val position: Int,
    val notes: String?,
    val song: SongResponse
)

data class SetlistCreateRequest(
    val name: String,
    val description: String? = null,
    @SerializedName("service_date")
    val serviceDate: String? = null,
    @SerializedName("event_type")
    val eventType: String? = null,
    val songs: List<SetlistSongCreateRequest>? = null
)

data class SetlistSongCreateRequest(
    @SerializedName("song_id")
    val songId: String,
    val position: Int,
    val notes: String? = null
)

data class SetlistUpdateRequest(
    val name: String? = null,
    val description: String? = null,
    @SerializedName("service_date")
    val serviceDate: String? = null,
    @SerializedName("event_type")
    val eventType: String? = null,
    val songs: List<SetlistSongCreateRequest>? = null
)
