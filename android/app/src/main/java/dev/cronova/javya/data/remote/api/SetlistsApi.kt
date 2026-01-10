package dev.cronova.javya.data.remote.api

import dev.cronova.javya.data.remote.dto.setlist.SetlistCreateRequest
import dev.cronova.javya.data.remote.dto.setlist.SetlistDetailResponse
import dev.cronova.javya.data.remote.dto.setlist.SetlistResponse
import dev.cronova.javya.data.remote.dto.setlist.SetlistUpdateRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface SetlistsApi {

    @GET("api/v1/setlists")
    suspend fun getSetlists(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50,
        @Query("search") search: String? = null,
        @Query("event_type") eventType: String? = null
    ): Response<List<SetlistResponse>>

    @GET("api/v1/setlists/{id}")
    suspend fun getSetlist(
        @Path("id") id: String
    ): Response<SetlistDetailResponse>

    @POST("api/v1/setlists")
    suspend fun createSetlist(
        @Body request: SetlistCreateRequest
    ): Response<SetlistDetailResponse>

    @PUT("api/v1/setlists/{id}")
    suspend fun updateSetlist(
        @Path("id") id: String,
        @Body request: SetlistUpdateRequest
    ): Response<SetlistDetailResponse>

    @DELETE("api/v1/setlists/{id}")
    suspend fun deleteSetlist(
        @Path("id") id: String
    ): Response<Unit>
}
