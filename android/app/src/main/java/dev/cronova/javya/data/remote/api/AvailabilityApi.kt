package dev.cronova.javya.data.remote.api

import dev.cronova.javya.data.remote.dto.availability.AvailabilityCreateRequest
import dev.cronova.javya.data.remote.dto.availability.AvailabilityPatternCreateRequest
import dev.cronova.javya.data.remote.dto.availability.AvailabilityPatternResponse
import dev.cronova.javya.data.remote.dto.availability.AvailabilityPatternUpdateRequest
import dev.cronova.javya.data.remote.dto.availability.AvailabilityResponse
import dev.cronova.javya.data.remote.dto.availability.BulkAvailabilityRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface AvailabilityApi {

    @POST("api/v1/availability")
    suspend fun createAvailability(
        @Body request: AvailabilityCreateRequest
    ): Response<AvailabilityResponse>

    @POST("api/v1/availability/bulk")
    suspend fun createBulkAvailability(
        @Body request: BulkAvailabilityRequest
    ): Response<List<AvailabilityResponse>>

    @GET("api/v1/availability/me")
    suspend fun getMyAvailability(
        @Query("start_date") startDate: String,
        @Query("end_date") endDate: String
    ): Response<List<AvailabilityResponse>>

    @GET("api/v1/availability/team")
    suspend fun getTeamAvailability(
        @Query("start_date") startDate: String,
        @Query("end_date") endDate: String
    ): Response<List<AvailabilityResponse>>

    @DELETE("api/v1/availability/{id}")
    suspend fun deleteAvailability(
        @Path("id") id: String
    ): Response<Unit>

    // Patterns
    @POST("api/v1/availability/patterns")
    suspend fun createPattern(
        @Body request: AvailabilityPatternCreateRequest
    ): Response<AvailabilityPatternResponse>

    @GET("api/v1/availability/patterns")
    suspend fun getPatterns(): Response<List<AvailabilityPatternResponse>>

    @PUT("api/v1/availability/patterns/{id}")
    suspend fun updatePattern(
        @Path("id") id: String,
        @Body request: AvailabilityPatternUpdateRequest
    ): Response<AvailabilityPatternResponse>

    @DELETE("api/v1/availability/patterns/{id}")
    suspend fun deletePattern(
        @Path("id") id: String
    ): Response<Unit>
}
