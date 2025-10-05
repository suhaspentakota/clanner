import base64
from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.providers.stt_openai import openai_stt
from app.providers.voice_openai import openai_tts
from app.routers.chat import ChatRequest, chat as chat_handler
from app.affect import classify_emotion_with_llm, simple_emotion_heuristic, detect_language, pick_voice_for_emotion, emotion_tone_instruction

router = APIRouter(tags=["voice"])

class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = None
    emotion: Optional[str] = None
    voice: Optional[str] = None
    audio_format: str = "mp3"
    model: Optional[str] = None

class TTSResponse(BaseModel):
    audio_b64: str
    audio_format: str
    voice: str
    emotion: str
    language: str

@router.post("/voice/stt")
async def stt_endpoint(audio: UploadFile = File(...), hint_language: Optional[str] = Form(None)):
    audio_bytes = await audio.read()
    text, lang = openai_stt(audio_bytes, filename=audio.filename or "audio.webm", hint_language=hint_language)
    if not lang:
        lang = detect_language(text or "")
    return {"text": text, "language": lang}

@router.post("/voice/tts", response_model=TTSResponse)
async def tts_endpoint(req: TTSRequest):
    emotion = req.emotion or "neutral"
    lang = req.language or "en"
    voice = req.voice or pick_voice_for_emotion(emotion)
    audio = openai_tts(req.text, voice=voice, audio_format=req.audio_format, model=req.model)
    return {"audio_b64": base64.b64encode(audio).decode("utf-8"), "audio_format": req.audio_format, "voice": voice, "emotion": emotion, "language": lang}

class VoiceChatResponse(BaseModel):
    transcript: str
    language: str
    emotion: str
    reply_text: str
    audio_b64: str
    audio_format: str = "mp3"
    voice: str
    citations: Optional[List[Dict[str, str]]] = None
    provider_traces: Optional[List[Dict[str, Any]]] = None

@router.post("/voice/chat", response_model=VoiceChatResponse)
async def voice_chat(audio: UploadFile = File(...), mode: str = Form("mix_ai"), model: Optional[str] = Form(None), search: bool = Form(False), retrieval: bool = Form(False), max_tokens: int = Form(600), temperature: float = Form(0.2), hint_language: Optional[str] = Form(None)):
    audio_bytes = await audio.read()
    transcript, lang = openai_stt(audio_bytes, filename=audio.filename or "audio.webm", hint_language=hint_language)
    lang = lang or detect_language(transcript or "")
    emotion = classify_emotion_with_llm(transcript, language=lang) or simple_emotion_heuristic(transcript)
    system_tone = emotion_tone_instruction(emotion, language_code=lang)
    messages = [{"role": "system", "content": f"You are Clanner, a helpful voice assistant. {system_tone}"},{"role": "user", "content": transcript}]
    chat_req = ChatRequest(messages=[type("Msg", (), m) for m in messages], mode=mode, model=model, search=search, retrieval=retrieval, max_tokens=max_tokens, temperature=temperature)
    chat_res = chat_handler(chat_req)
    reply_text = chat_res.output
    voice = pick_voice_for_emotion(emotion)
    audio_bytes_out = openai_tts(reply_text, voice=voice, audio_format="mp3", model=None)
    return VoiceChatResponse(transcript=transcript, language=lang, emotion=emotion, reply_text=reply_text, audio_b64=base64.b64encode(audio_bytes_out).decode("utf-8"), audio_format="mp3", voice=voice, citations=chat_res.citations, provider_traces=chat_res.provider_traces)
