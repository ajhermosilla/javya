package dev.cronova.javya.data.remote.dto.auth

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val username: String, // Email is used as username
    val password: String
)

data class RegisterRequest(
    val email: String,
    val password: String,
    val name: String
)

data class TokenResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String
)

data class UserResponse(
    val id: String,
    val email: String,
    val name: String,
    val role: String,
    @SerializedName("is_active")
    val isActive: Boolean,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)
