package com.clanner
import android.Manifest
import android.media.MediaPlayer
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import com.clanner.api.*
import com.clanner.audio.AudioRecorder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import android.util.Base64
import java.io.File
import java.io.FileOutputStream

class MainActivity : ComponentActivity() {
    private lateinit var recorder: AudioRecorder
    private var mediaPlayer: MediaPlayer? = null
    private val micPermissionLauncher = registerForActivityResult(ActivityResultContracts.RequestPermission()) { _ -> }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        recorder = AudioRecorder(this)
        setContent { AppUI() }
        micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
    }
    @OptIn(ExperimentalMaterial3Api::class)
    @Composable
    fun AppUI() {
        val scope = rememberCoroutineScope()
        var input by remember { mutableStateOf(TextFieldValue("")) }
        var chatOut by remember { mutableStateOf("") }
        var providers by remember { mutableStateOf(listOf<ProviderTrace>()) }
        var citations by remember { mutableStateOf(listOf<Citation>()) }
        var busy by remember { mutableStateOf(false) }
        var recording by remember { mutableStateOf(false) }
        var emotion by remember { mutableStateOf("") }
        var language by remember { mutableStateOf("") }
        var transcript by remember { mutableStateOf("") }
        fun playBase64Mp3(b64: String) {
            try {
                val bytes = Base64.decode(b64, Base64.DEFAULT)
                val outFile = File.createTempFile("clanner_reply_", ".mp3", cacheDir)
                FileOutputStream(outFile).use { it.write(bytes) }
                mediaPlayer?.release()
                mediaPlayer = MediaPlayer().apply { setDataSource(outFile.absolutePath); prepare(); start() }
            } catch (_: Exception) { }
        }
        Scaffold(topBar = { TopAppBar(title = { Text("Clanner (Android)") }) }) { pad ->
            Column(Modifier.padding(pad).padding(16.dp).fillMaxSize()) {
                Text("Chat", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(value = input, onValueChange = { input = it }, placeholder = { Text("Ask anything…") }, modifier = Modifier.fillMaxWidth())
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Button(enabled = !busy && input.text.isNotBlank(), onClick = {
                        val text = input.text
                        scope.launch(Dispatchers.IO) {
                            try {
                                busy = true
                                val payload = ChatPayload(messages = listOf(ChatMessage("system","You are Clanner, helpful and concise."), ChatMessage("user", text)), mode = "mix_ai", search = false, retrieval = false)
                                val resp = ApiClient.api.chat(payload)
                                chatOut = resp.output; providers = resp.provider_traces ?: emptyList(); citations = resp.citations ?: emptyList()
                            } catch (e: Exception) { chatOut = "Error: ${e.message}" } finally { busy = false }
                        }
                    }) { Text("Send") }
                    Spacer(Modifier.width(12.dp))
                    if (busy) CircularProgressIndicator(Modifier.size(22.dp))
                }
                Spacer(Modifier.height(8.dp))
                Text(chatOut)
                if (providers.isNotEmpty()) { Spacer(Modifier.height(8.dp)); Text("Providers:", style = MaterialTheme.typography.labelLarge); providers.forEach { p -> Text("- ${p.provider} (${p.model}) • ${p.latency_ms} ms") } }
                if (citations.isNotEmpty()) { Spacer(Modifier.height(8.dp)); Text("Citations:", style = MaterialTheme.typTypography.labelLarge); citations.forEach { c -> Text("- ${c.title} • ${c.url}") } }
                Spacer(Modifier.height(24.dp)); Divider(); Spacer(Modifier.height(16.dp))
                Text("Voice (any language, Mix AI + artificial feelings)", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Button(enabled = !busy, onClick = {
                        if (!recording) { recorder.start(); recording = true }
                        else {
                            val file = recorder.stop(); recording = false
                            if (file != null) {
                                scope.launch(Dispatchers.IO) {
                                    try {
                                        busy = true
                                        val reqBody = RequestBody.create("audio/m4a".toMediaTypeOrNull(), file)
                                        val part = MultipartBody.Part.createFormData("audio", file.name, reqBody)
                                        val resp = ApiClient.api.voiceChat(audio = part, mode = "mix_ai", search = false, retrieval = false, hintLanguage = null)
                                        transcript = resp.transcript; language = resp.language; emotion = resp.emotion; chatOut = resp.reply_text
                                        providers = resp.provider_traces ?: emptyList(); citations = resp.citations ?: emptyList()
                                        playBase64Mp3(resp.audio_b64)
                                    } catch (e: Exception) { chatOut = "Voice error: ${e.message}" } finally { busy = false; file.delete() }
                                }
                            }
                        }
                    }) { Text(if (!recording) "Record" else "Stop") }
                    Spacer(Modifier.width(12.dp))
                    if (busy) CircularProgressIndicator(Modifier.size(22.dp))
                }
                if (transcript.isNotBlank()) { Spacer(Modifier.height(8.dp)); Text("Transcript (${language}) • Emotion: ${emotion}"); Text(transcript) }
                Spacer(Modifier.height(12.dp))
                Text("Reply:"); Text(chatOut, modifier = Modifier.verticalScroll(rememberScrollState()))
            }
        }
    }
    override fun onDestroy() { super.onDestroy(); mediaPlayer?.release() }
}
