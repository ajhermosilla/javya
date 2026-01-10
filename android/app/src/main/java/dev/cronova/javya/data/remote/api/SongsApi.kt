package dev.cronova.javya.data.remote.api

import dev.cronova.javya.data.remote.dto.song.SongCreateRequest
import dev.cronova.javya.data.remote.dto.song.SongResponse
import dev.cronova.javya.data.remote.dto.song.SongUpdateRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface SongsApi {

    @GET("api/v1/songs")
    suspend fun getSongs(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50,
        @Query("search") search: String? = null,
        @Query("key") key: String? = null,
        @Query("mood") mood: String? = null,
        @Query("theme") theme: String? = null
    ): Response<List<SongResponse>>

    @GET("api/v1/songs/{id}")
    suspend fun getSong(
        @Path("id") id: String
    ): Response<SongResponse>

    @POST("api/v1/songs")
    suspend fun createSong(
        @Body request: SongCreateRequest
    ): Response<SongResponse>

    @PUT("api/v1/songs/{id}")
    suspend fun updateSong(
        @Path("id") id: String,
        @Body request: SongUpdateRequest
    ): Response<SongResponse>

    @DELETE("api/v1/songs/{id}")
    suspend fun deleteSong(
        @Path("id") id: String
    ): Response<Unit>
}
