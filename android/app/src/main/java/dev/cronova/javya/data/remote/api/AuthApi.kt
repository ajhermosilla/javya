package dev.cronova.javya.data.remote.api

import dev.cronova.javya.data.remote.dto.auth.LoginRequest
import dev.cronova.javya.data.remote.dto.auth.RegisterRequest
import dev.cronova.javya.data.remote.dto.auth.TokenResponse
import dev.cronova.javya.data.remote.dto.auth.UserResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.POST

interface AuthApi {

    @FormUrlEncoded
    @POST("api/v1/auth/login")
    suspend fun login(
        @Field("username") email: String,
        @Field("password") password: String
    ): Response<TokenResponse>

    @POST("api/v1/auth/register")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<UserResponse>

    @GET("api/v1/auth/me")
    suspend fun getCurrentUser(): Response<UserResponse>
}
