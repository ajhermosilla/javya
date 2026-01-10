package dev.cronova.javya.data.remote.dto.song

import com.google.gson.annotations.SerializedName

data class SongResponse(
    val id: String,
    val name: String,
    val artist: String?,
    val url: String?,
    @SerializedName("original_key")
    val originalKey: String?,
    @SerializedName("preferred_key")
    val preferredKey: String?,
    @SerializedName("tempo_bpm")
    val tempoBpm: Int?,
    val mood: String?,
    val themes: List<String>?,
    val lyrics: String?,
    @SerializedName("chordpro_chart")
    val chordproChart: String?,
    @SerializedName("min_band")
    val minBand: List<String>?,
    val notes: String?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class SongCreateRequest(
    val name: String,
    val artist: String? = null,
    val url: String? = null,
    @SerializedName("original_key")
    val originalKey: String? = null,
    @SerializedName("preferred_key")
    val preferredKey: String? = null,
    @SerializedName("tempo_bpm")
    val tempoBpm: Int? = null,
    val mood: String? = null,
    val themes: List<String>? = null,
    val lyrics: String? = null,
    @SerializedName("chordpro_chart")
    val chordproChart: String? = null,
    @SerializedName("min_band")
    val minBand: List<String>? = null,
    val notes: String? = null
)

data class SongUpdateRequest(
    val name: String? = null,
    val artist: String? = null,
    val url: String? = null,
    @SerializedName("original_key")
    val originalKey: String? = null,
    @SerializedName("preferred_key")
    val preferredKey: String? = null,
    @SerializedName("tempo_bpm")
    val tempoBpm: Int? = null,
    val mood: String? = null,
    val themes: List<String>? = null,
    val lyrics: String? = null,
    @SerializedName("chordpro_chart")
    val chordproChart: String? = null,
    @SerializedName("min_band")
    val minBand: List<String>? = null,
    val notes: String? = null
)
