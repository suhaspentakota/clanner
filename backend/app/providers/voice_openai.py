import httpx
from typing import Optional
from app.config import settings

def openai_tts(text: str, voice: str = "alloy", audio_format: str = "mp3", model: Optional[str] = None) -> bytes:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")
    url="https://api.openai.com/v1/audio/speech"
    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    payload={"model": model or "gpt-4o-mini-tts","input": text,"voice": voice,"format": audio_format}
    resp=httpx.post(url,headers=headers,json=payload,timeout=120)
    resp.raise_for_status()
    return resp.content
