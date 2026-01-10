package dev.cronova.javya.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dev.cronova.javya.data.remote.dto.auth.UserResponse
import dev.cronova.javya.data.repository.AuthRepository
import dev.cronova.javya.data.repository.Result
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the authentication screen.
 */
data class AuthUiState(
    val isLoading: Boolean = false,
    val isLoginMode: Boolean = true,
    val email: String = "",
    val password: String = "",
    val name: String = "",
    val emailError: String? = null,
    val passwordError: String? = null,
    val nameError: String? = null,
    val generalError: String? = null,
    val user: UserResponse? = null
)

/**
 * Events emitted by AuthViewModel.
 */
sealed class AuthEvent {
    object NavigateToHome : AuthEvent()
    data class ShowError(val message: String) : AuthEvent()
}

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    private val _events = MutableStateFlow<AuthEvent?>(null)
    val events: StateFlow<AuthEvent?> = _events.asStateFlow()

    val isLoggedIn: StateFlow<Boolean> = authRepository.isLoggedIn
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = false
        )

    fun onEmailChange(email: String) {
        _uiState.value = _uiState.value.copy(
            email = email,
            emailError = null,
            generalError = null
        )
    }

    fun onPasswordChange(password: String) {
        _uiState.value = _uiState.value.copy(
            password = password,
            passwordError = null,
            generalError = null
        )
    }

    fun onNameChange(name: String) {
        _uiState.value = _uiState.value.copy(
            name = name,
            nameError = null,
            generalError = null
        )
    }

    fun toggleMode() {
        _uiState.value = _uiState.value.copy(
            isLoginMode = !_uiState.value.isLoginMode,
            emailError = null,
            passwordError = null,
            nameError = null,
            generalError = null
        )
    }

    fun submit() {
        val state = _uiState.value

        // Validate
        var hasError = false

        if (state.email.isBlank()) {
            _uiState.value = _uiState.value.copy(emailError = "Email is required")
            hasError = true
        } else if (!isValidEmail(state.email)) {
            _uiState.value = _uiState.value.copy(emailError = "Invalid email format")
            hasError = true
        }

        if (state.password.isBlank()) {
            _uiState.value = _uiState.value.copy(passwordError = "Password is required")
            hasError = true
        } else if (state.password.length < 8) {
            _uiState.value = _uiState.value.copy(passwordError = "Password must be at least 8 characters")
            hasError = true
        }

        if (!state.isLoginMode && state.name.isBlank()) {
            _uiState.value = _uiState.value.copy(nameError = "Name is required")
            hasError = true
        }

        if (hasError) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, generalError = null)

            val result = if (state.isLoginMode) {
                authRepository.login(state.email.trim(), state.password)
            } else {
                authRepository.register(state.email.trim(), state.password, state.name.trim())
            }

            when (result) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        user = result.data
                    )
                    _events.value = AuthEvent.NavigateToHome
                }
                is Result.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        generalError = result.message
                    )
                }
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _uiState.value = AuthUiState()
        }
    }

    fun clearEvent() {
        _events.value = null
    }

    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}
