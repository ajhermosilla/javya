package dev.cronova.javya.data.repository

import dev.cronova.javya.data.local.database.dao.UserDao
import dev.cronova.javya.data.local.database.entity.UserEntity
import dev.cronova.javya.data.local.datastore.AuthDataStore
import dev.cronova.javya.data.remote.api.AuthApi
import dev.cronova.javya.data.remote.dto.auth.RegisterRequest
import dev.cronova.javya.data.remote.dto.auth.UserResponse
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Result wrapper for repository operations.
 */
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val code: Int? = null) : Result<Nothing>()
}

/**
 * Repository for authentication operations.
 */
interface AuthRepository {
    val isLoggedIn: Flow<Boolean>

    suspend fun login(email: String, password: String): Result<UserResponse>
    suspend fun register(email: String, password: String, name: String): Result<UserResponse>
    suspend fun getCurrentUser(): Result<UserResponse>
    suspend fun logout()

    fun getUserId(): String?
    fun getUserRole(): String?
}

@Singleton
class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi,
    private val authDataStore: AuthDataStore,
    private val userDao: UserDao
) : AuthRepository {

    override val isLoggedIn: Flow<Boolean> = authDataStore.isLoggedIn

    override suspend fun login(email: String, password: String): Result<UserResponse> {
        return try {
            val response = authApi.login(email, password)

            if (response.isSuccessful && response.body() != null) {
                val tokenResponse = response.body()!!
                authDataStore.saveToken(tokenResponse.accessToken)

                // Fetch user details after login
                val userResult = getCurrentUser()
                if (userResult is Result.Success) {
                    userResult
                } else {
                    // Token saved but couldn't get user - still consider success
                    Result.Error("Login successful but couldn't fetch user details")
                }
            } else {
                val errorBody = response.errorBody()?.string()
                Result.Error(
                    message = parseErrorMessage(errorBody) ?: "Login failed",
                    code = response.code()
                )
            }
        } catch (e: Exception) {
            Result.Error(message = e.message ?: "Network error")
        }
    }

    override suspend fun register(
        email: String,
        password: String,
        name: String
    ): Result<UserResponse> {
        return try {
            val response = authApi.register(RegisterRequest(email, password, name))

            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!

                // After registration, login to get token
                val loginResult = login(email, password)
                if (loginResult is Result.Success) {
                    Result.Success(user)
                } else {
                    // Registration succeeded but login failed
                    Result.Error("Registration successful. Please sign in.")
                }
            } else {
                val errorBody = response.errorBody()?.string()
                Result.Error(
                    message = parseErrorMessage(errorBody) ?: "Registration failed",
                    code = response.code()
                )
            }
        } catch (e: Exception) {
            Result.Error(message = e.message ?: "Network error")
        }
    }

    override suspend fun getCurrentUser(): Result<UserResponse> {
        return try {
            val response = authApi.getCurrentUser()

            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!

                // Save user info locally
                authDataStore.saveUserId(user.id)
                authDataStore.saveUserEmail(user.email)
                authDataStore.saveUserName(user.name)
                authDataStore.saveUserRole(user.role)

                // Cache user in database
                userDao.insert(user.toEntity())

                Result.Success(user)
            } else {
                if (response.code() == 401) {
                    // Token expired or invalid
                    authDataStore.clearAll()
                }
                Result.Error(
                    message = "Failed to get user",
                    code = response.code()
                )
            }
        } catch (e: Exception) {
            Result.Error(message = e.message ?: "Network error")
        }
    }

    override suspend fun logout() {
        authDataStore.clearAll()
    }

    override fun getUserId(): String? = authDataStore.getUserId()

    override fun getUserRole(): String? = authDataStore.getUserRole()

    private fun parseErrorMessage(errorBody: String?): String? {
        if (errorBody.isNullOrBlank()) return null

        // Try to parse JSON error response
        return try {
            // Simple parsing for {"detail": "message"} format
            val detailMatch = Regex(""""detail"\s*:\s*"([^"]+)"""").find(errorBody)
            detailMatch?.groupValues?.get(1)
        } catch (e: Exception) {
            errorBody
        }
    }

    private fun UserResponse.toEntity() = UserEntity(
        id = id,
        email = email,
        name = name,
        role = role,
        isActive = isActive,
        createdAt = createdAt,
        updatedAt = updatedAt
    )
}
