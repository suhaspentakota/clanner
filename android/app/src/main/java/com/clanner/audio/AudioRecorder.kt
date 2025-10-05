package com.clanner.audio
import android.content.Context
import android.media.MediaRecorder
import java.io.File

class AudioRecorder(private val context: Context) {
    private var recorder: MediaRecorder? = null
    private var file: File? = null
    fun start(): File {
        stop()
        val out = File.createTempFile("clanner_", ".m4a", context.cacheDir)
        val r = MediaRecorder()
        r.setAudioSource(MediaRecorder.AudioSource.MIC)
        r.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
        r.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
        r.setAudioEncodingBitRate(128_000)
        r.setAudioSamplingRate(44_100)
        r.setOutputFile(out.absolutePath)
        r.prepare()
        r.start()
        recorder = r; file = out
        return out
    }
    fun stop(): File? {
        try { recorder?.apply { stop(); reset(); release() } } catch (_: Exception) {}
        val f = file; recorder = null; file = null; return f
    }
}
