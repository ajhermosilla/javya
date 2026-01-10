package dev.cronova.javya.ui.auth

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusDirection
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import dev.cronova.javya.R

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    viewModel: AuthViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val event by viewModel.events.collectAsState()
    val focusManager = LocalFocusManager.current

    var passwordVisible by remember { mutableStateOf(false) }

    // Handle navigation events
    LaunchedEffect(event) {
        when (event) {
            is AuthEvent.NavigateToHome -> {
                viewModel.clearEvent()
                onLoginSuccess()
            }
            is AuthEvent.ShowError -> {
                viewModel.clearEvent()
            }
            null -> {}
        }
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .imePadding()
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                // Logo / Title
                Text(
                    text = stringResource(R.string.app_name),
                    style = MaterialTheme.typography.displaySmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = stringResource(R.string.app_tagline),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(48.dp))

                // Title
                Text(
                    text = if (uiState.isLoginMode) {
                        stringResource(R.string.auth_login)
                    } else {
                        stringResource(R.string.auth_register)
                    },
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.SemiBold
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Name field (only for registration)
                AnimatedVisibility(visible = !uiState.isLoginMode) {
                    Column {
                        OutlinedTextField(
                            value = uiState.name,
                            onValueChange = viewModel::onNameChange,
                            label = { Text(stringResource(R.string.auth_name)) },
                            leadingIcon = {
                                Icon(Icons.Default.Person, contentDescription = null)
                            },
                            isError = uiState.nameError != null,
                            supportingText = uiState.nameError?.let { { Text(it) } },
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(
                                keyboardType = KeyboardType.Text,
                                imeAction = ImeAction.Next
                            ),
                            keyboardActions = KeyboardActions(
                                onNext = { focusManager.moveFocus(FocusDirection.Down) }
                            ),
                            modifier = Modifier.fillMaxWidth()
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }

                // Email field
                OutlinedTextField(
                    value = uiState.email,
                    onValueChange = viewModel::onEmailChange,
                    label = { Text(stringResource(R.string.auth_email)) },
                    leadingIcon = {
                        Icon(Icons.Default.Email, contentDescription = null)
                    },
                    isError = uiState.emailError != null,
                    supportingText = uiState.emailError?.let { { Text(it) } },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Email,
                        imeAction = ImeAction.Next
                    ),
                    keyboardActions = KeyboardActions(
                        onNext = { focusManager.moveFocus(FocusDirection.Down) }
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Password field
                OutlinedTextField(
                    value = uiState.password,
                    onValueChange = viewModel::onPasswordChange,
                    label = { Text(stringResource(R.string.auth_password)) },
                    leadingIcon = {
                        Icon(Icons.Default.Lock, contentDescription = null)
                    },
                    trailingIcon = {
                        IconButton(onClick = { passwordVisible = !passwordVisible }) {
                            Icon(
                                imageVector = if (passwordVisible) {
                                    Icons.Default.VisibilityOff
                                } else {
                                    Icons.Default.Visibility
                                },
                                contentDescription = if (passwordVisible) {
                                    "Hide password"
                                } else {
                                    "Show password"
                                }
                            )
                        }
                    },
                    visualTransformation = if (passwordVisible) {
                        VisualTransformation.None
                    } else {
                        PasswordVisualTransformation()
                    },
                    isError = uiState.passwordError != null,
                    supportingText = uiState.passwordError?.let { { Text(it) } },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Password,
                        imeAction = ImeAction.Done
                    ),
                    keyboardActions = KeyboardActions(
                        onDone = {
                            focusManager.clearFocus()
                            viewModel.submit()
                        }
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                // General error message
                AnimatedVisibility(visible = uiState.generalError != null) {
                    Column {
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = uiState.generalError ?: "",
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodySmall,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Submit button
                Button(
                    onClick = viewModel::submit,
                    enabled = !uiState.isLoading,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                ) {
                    if (uiState.isLoading) {
                        CircularProgressIndicator(
                            color = MaterialTheme.colorScheme.onPrimary,
                            strokeWidth = 2.dp,
                            modifier = Modifier.height(24.dp)
                        )
                    } else {
                        Text(
                            text = if (uiState.isLoginMode) {
                                stringResource(R.string.auth_login)
                            } else {
                                stringResource(R.string.auth_register)
                            }
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Toggle between login and register
                TextButton(onClick = viewModel::toggleMode) {
                    Text(
                        text = if (uiState.isLoginMode) {
                            stringResource(R.string.auth_no_account)
                        } else {
                            stringResource(R.string.auth_have_account)
                        }
                    )
                }
            }
        }
    }
}
