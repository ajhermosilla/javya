package dev.cronova.javya.data.repository

import com.google.common.truth.Truth.assertThat
import dev.cronova.javya.data.local.database.dao.UserDao
import dev.cronova.javya.data.local.datastore.AuthDataStore
import dev.cronova.javya.data.remote.api.AuthApi
import dev.cronova.javya.data.remote.dto.auth.TokenResponse
import dev.cronova.javya.data.remote.dto.auth.UserResponse
import dev.cronova.javya.util.MainDispatcherRule
import dev.cronova.javya.util.TestData
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.Mock
import org.mockito.Mockito.anyString
import org.mockito.Mockito.never
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import retrofit2.Response

/**
 * Unit tests for AuthRepositoryImpl.
 *
 * Tests authentication flows using mocked dependencies.
 */
class AuthRepositoryTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Mock
    private lateinit var authApi: AuthApi

    @Mock
    private lateinit var authDataStore: AuthDataStore

    @Mock
    private lateinit var userDao: UserDao

    private lateinit var authRepository: AuthRepositoryImpl

    private val isLoggedInFlow = MutableStateFlow(false)

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        `when`(authDataStore.isLoggedIn).thenReturn(isLoggedInFlow)
        authRepository = AuthRepositoryImpl(authApi, authDataStore, userDao)
    }

    // ==================== Login Tests ====================

    @Test
    fun `login with valid credentials returns success`() = runTest {
        // Arrange
        val tokenResponse = TestData.createTokenResponse()
        val userResponse = TestData.createUserResponse()

        `when`(authApi.login(anyString(), anyString()))
            .thenReturn(Response.success(tokenResponse))
        `when`(authApi.getCurrentUser())
            .thenReturn(Response.success(userResponse))

        // Act
        val result = authRepository.login("test@example.com", "password123")

        // Assert
        assertThat(result).isInstanceOf(Result.Success::class.java)
        val success = result as Result.Success
        assertThat(success.data.email).isEqualTo("test@example.com")

        verify(authDataStore).saveToken(tokenResponse.accessToken)
        verify(authDataStore).saveUserId(userResponse.id)
        verify(userDao).insert(any())
    }

    @Test
    fun `login with invalid credentials returns error`() = runTest {
        // Arrange
        val errorBody = """{"detail": "Incorrect email or password"}""".toResponseBody()
        `when`(authApi.login(anyString(), anyString()))
            .thenReturn(Response.error(401, errorBody))

        // Act
        val result = authRepository.login("test@example.com", "wrongpassword")

        // Assert
        assertThat(result).isInstanceOf(Result.Error::class.java)
        val error = result as Result.Error
        assertThat(error.code).isEqualTo(401)
        assertThat(error.message).contains("Incorrect email or password")

        verify(authDataStore, never()).saveToken(anyString())
    }

    @Test
    fun `login with network error returns error`() = runTest {
        // Arrange
        `when`(authApi.login(anyString(), anyString()))
            .thenThrow(RuntimeException("Network error"))

        // Act
        val result = authRepository.login("test@example.com", "password123")

        // Assert
        assertThat(result).isInstanceOf(Result.Error::class.java)
        val error = result as Result.Error
        assertThat(error.message).contains("Network error")
    }

    // ==================== Register Tests ====================

    @Test
    fun `register with valid data returns success`() = runTest {
        // Arrange
        val userResponse = TestData.createUserResponse()
        val tokenResponse = TestData.createTokenResponse()

        `when`(authApi.register(any()))
            .thenReturn(Response.success(userResponse))
        `when`(authApi.login(anyString(), anyString()))
            .thenReturn(Response.success(tokenResponse))
        `when`(authApi.getCurrentUser())
            .thenReturn(Response.success(userResponse))

        // Act
        val result = authRepository.register("test@example.com", "password123", "Test User")

        // Assert
        assertThat(result).isInstanceOf(Result.Success::class.java)
        val success = result as Result.Success
        assertThat(success.data.email).isEqualTo("test@example.com")
    }

    @Test
    fun `register with existing email returns error`() = runTest {
        // Arrange
        val errorBody = """{"detail": "Email already registered"}""".toResponseBody()
        `when`(authApi.register(any()))
            .thenReturn(Response.error(400, errorBody))

        // Act
        val result = authRepository.register("existing@example.com", "password123", "Test User")

        // Assert
        assertThat(result).isInstanceOf(Result.Error::class.java)
        val error = result as Result.Error
        assertThat(error.message).contains("Email already registered")
    }

    // ==================== Get Current User Tests ====================

    @Test
    fun `getCurrentUser with valid token returns user`() = runTest {
        // Arrange
        val userResponse = TestData.createUserResponse()
        `when`(authApi.getCurrentUser())
            .thenReturn(Response.success(userResponse))

        // Act
        val result = authRepository.getCurrentUser()

        // Assert
        assertThat(result).isInstanceOf(Result.Success::class.java)
        val success = result as Result.Success
        assertThat(success.data.id).isEqualTo(userResponse.id)

        verify(authDataStore).saveUserId(userResponse.id)
        verify(authDataStore).saveUserEmail(userResponse.email)
        verify(authDataStore).saveUserName(userResponse.name)
        verify(authDataStore).saveUserRole(userResponse.role)
        verify(userDao).insert(any())
    }

    @Test
    fun `getCurrentUser with expired token clears auth and returns error`() = runTest {
        // Arrange
        val errorBody = """{"detail": "Token expired"}""".toResponseBody()
        `when`(authApi.getCurrentUser())
            .thenReturn(Response.error(401, errorBody))

        // Act
        val result = authRepository.getCurrentUser()

        // Assert
        assertThat(result).isInstanceOf(Result.Error::class.java)
        val error = result as Result.Error
        assertThat(error.code).isEqualTo(401)

        verify(authDataStore).clearAll()
    }

    // ==================== Logout Tests ====================

    @Test
    fun `logout clears all auth data`() = runTest {
        // Act
        authRepository.logout()

        // Assert
        verify(authDataStore).clearAll()
    }

    // ==================== Helper Method Tests ====================

    @Test
    fun `getUserId returns value from data store`() {
        // Arrange
        `when`(authDataStore.getUserId()).thenReturn("user-123")

        // Act
        val result = authRepository.getUserId()

        // Assert
        assertThat(result).isEqualTo("user-123")
    }

    @Test
    fun `getUserRole returns value from data store`() {
        // Arrange
        `when`(authDataStore.getUserRole()).thenReturn("admin")

        // Act
        val result = authRepository.getUserRole()

        // Assert
        assertThat(result).isEqualTo("admin")
    }

    // ==================== isLoggedIn Flow Tests ====================

    @Test
    fun `isLoggedIn returns flow from data store`() = runTest {
        // The flow should reflect the state from authDataStore
        assertThat(authRepository.isLoggedIn).isEqualTo(isLoggedInFlow)
    }
}
