package dev.cronova.javya.di

import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import dev.cronova.javya.BuildConfig
import dev.cronova.javya.data.local.datastore.AuthDataStore
import dev.cronova.javya.data.remote.api.AuthApi
import dev.cronova.javya.data.remote.api.AvailabilityApi
import dev.cronova.javya.data.remote.api.SchedulingApi
import dev.cronova.javya.data.remote.api.SetlistsApi
import dev.cronova.javya.data.remote.api.SongsApi
import dev.cronova.javya.data.remote.interceptor.AuthInterceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    // TODO: Make this configurable via settings
    private const val BASE_URL = "http://10.0.2.2:8000/" // Android emulator localhost

    @Provides
    @Singleton
    fun provideAuthInterceptor(
        authDataStore: AuthDataStore
    ): AuthInterceptor = AuthInterceptor(authDataStore)

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        val builder = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)

        if (BuildConfig.DEBUG) {
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            builder.addInterceptor(loggingInterceptor)
        }

        return builder.build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient
    ): Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi =
        retrofit.create(AuthApi::class.java)

    @Provides
    @Singleton
    fun provideSongsApi(retrofit: Retrofit): SongsApi =
        retrofit.create(SongsApi::class.java)

    @Provides
    @Singleton
    fun provideSetlistsApi(retrofit: Retrofit): SetlistsApi =
        retrofit.create(SetlistsApi::class.java)

    @Provides
    @Singleton
    fun provideAvailabilityApi(retrofit: Retrofit): AvailabilityApi =
        retrofit.create(AvailabilityApi::class.java)

    @Provides
    @Singleton
    fun provideSchedulingApi(retrofit: Retrofit): SchedulingApi =
        retrofit.create(SchedulingApi::class.java)
}
