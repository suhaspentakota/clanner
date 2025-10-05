package com.clanner.api
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

interface ClannerApi {
    @POST("chat") suspend fun chat(@Body body: ChatPayload): ChatResponse
    @Multipart @POST("voice/chat")
    suspend fun voiceChat(@Part audio: MultipartBody.Part, @Part("mode") mode: String = "mix_ai", @Part("search") search: Boolean = false, @Part("retrieval") retrieval: Boolean = false, @Part("max_tokens") maxTokens: Int = 600, @Part("temperature") temperature: Double = 0.2, @Part("hint_language") hintLanguage: String? = null, @Part("model") model: String? = null): VoiceChatResponse
}
object ApiClient {
    private const val BASE_URL = "http://10.0.2.2:8000/v1/"
    private val logging = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BASIC }
    private val http = OkHttpClient.Builder().addInterceptor(logging).build()
    val api: ClannerApi = Retrofit.Builder().baseUrl(BASE_URL).client(http).addConverterFactory(GsonConverterFactory.create()).build().create(ClannerApi::class.java)
}
