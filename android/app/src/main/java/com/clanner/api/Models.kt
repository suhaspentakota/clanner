package com.clanner.api
data class ChatMessage(val role: String, val content: String)
data class ChatPayload(val messages: List<ChatMessage>, val mode: String = "mix_ai", val model: String? = null, val search: Boolean = false, val retrieval: Boolean = false, val max_tokens: Int = 800, val temperature: Double = 0.2)
data class Citation(val title: String, val url: String)
data class ProviderTrace(val provider: String, val model: String, val latency_ms: Int)
data class ChatResponse(val output: String, val citations: List<Citation>?, val provider_traces: List<ProviderTrace>?)
data class VoiceChatResponse(val transcript: String, val language: String, val emotion: String, val reply_text: String, val audio_b64: String, val audio_format: String, val voice: String, val citations: List<Citation>?, val provider_traces: List<ProviderTrace>?)
