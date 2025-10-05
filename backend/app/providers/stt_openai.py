import httpx
from typing import Optional, Tuple
from app.config import settings

def openai_stt(audio_bytes: bytes, filename: str = "audio.webm", hint_language: Optional[str] = None) -> Tuple[str, Optional[str]]:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")
    url="https://api.openai.com/v1/audio/transcriptions"
    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    files={"file": (filename, audio_bytes, "application/octet-stream"),"model": (None, "whisper-1"),"response_format": (None, "json")}
    if hint_language:
        files["language"]=(None,hint_language)
    resp=httpx.post(url,headers=headers,files=files,timeout=120)
    resp.raise_for_status()
    data=resp.json()
    text=data.get("text","") or ""
    language=data.get("language")
    return text, language
