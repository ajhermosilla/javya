package dev.cronova.javya.data.remote.api

import dev.cronova.javya.data.remote.dto.scheduling.CalendarSetlistResponse
import dev.cronova.javya.data.remote.dto.scheduling.MyAssignmentResponse
import dev.cronova.javya.data.remote.dto.scheduling.SetlistAssignmentCreateRequest
import dev.cronova.javya.data.remote.dto.scheduling.SetlistAssignmentResponse
import dev.cronova.javya.data.remote.dto.scheduling.SetlistAssignmentUpdateRequest
import dev.cronova.javya.data.remote.dto.scheduling.TeamAvailabilityResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface SchedulingApi {

    @GET("api/v1/scheduling/calendar")
    suspend fun getCalendar(
        @Query("start_date") startDate: String,
        @Query("end_date") endDate: String
    ): Response<List<CalendarSetlistResponse>>

    @GET("api/v1/scheduling/my-assignments")
    suspend fun getMyAssignments(
        @Query("upcoming_only") upcomingOnly: Boolean = true
    ): Response<List<MyAssignmentResponse>>

    @GET("api/v1/scheduling/team-availability")
    suspend fun getTeamAvailability(
        @Query("service_date") serviceDate: String
    ): Response<List<TeamAvailabilityResponse>>

    // Setlist assignments
    @GET("api/v1/setlists/{setlistId}/assignments")
    suspend fun getAssignments(
        @Path("setlistId") setlistId: String
    ): Response<List<SetlistAssignmentResponse>>

    @POST("api/v1/setlists/{setlistId}/assignments")
    suspend fun createAssignment(
        @Path("setlistId") setlistId: String,
        @Body request: SetlistAssignmentCreateRequest
    ): Response<SetlistAssignmentResponse>

    @PUT("api/v1/setlists/{setlistId}/assignments/{assignmentId}")
    suspend fun updateAssignment(
        @Path("setlistId") setlistId: String,
        @Path("assignmentId") assignmentId: String,
        @Body request: SetlistAssignmentUpdateRequest
    ): Response<SetlistAssignmentResponse>

    @DELETE("api/v1/setlists/{setlistId}/assignments/{assignmentId}")
    suspend fun deleteAssignment(
        @Path("setlistId") setlistId: String,
        @Path("assignmentId") assignmentId: String
    ): Response<Unit>

    @PATCH("api/v1/setlists/{setlistId}/assignments/{assignmentId}/confirm")
    suspend fun confirmAssignment(
        @Path("setlistId") setlistId: String,
        @Path("assignmentId") assignmentId: String,
        @Body confirmed: Map<String, Boolean>
    ): Response<SetlistAssignmentResponse>
}
