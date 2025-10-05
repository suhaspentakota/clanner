from typing import Optional
from langdetect import detect as detect_lang
from app.config import settings
from app.providers import openai as openai_provider

EMOTIONS = ["neutral","empathetic","cheerful","calm","excited","serious","sad","angry"]

def simple_emotion_heuristic(text: str) -> str:
    t=text.lower()
    if any(k in t for k in ["sorry","sad","depressed","upset","unhappy"]): return "empathetic"
    if any(k in t for k in ["wow","great","awesome","amazing","yay","love it"]): return "cheerful"
    if any(k in t for k in ["angry","mad","furious","annoyed"]): return "calm"
    if any(k in t for k in ["urgent","asap","hurry"]): return "serious"
    return "neutral"

def classify_emotion_with_llm(user_text: str, language: Optional[str]) -> Optional[str]:
    if not settings.OPENAI_API_KEY: return None
    sys=("You are an affect detector. Output ONE label from: " + ", ".join(EMOTIONS) + ".")
    messages=[{"role":"system","content":sys},{"role":"user","content":f"Language: {language or 'unknown'}\nUtterance: {user_text}"}]
    try:
        out=openai_provider.openai_chat(messages,max_tokens=5,temperature=0.0)
        label=(out["output"] or "").strip().split()[0].lower()
        if label in EMOTIONS: return label
    except Exception:
        return None
    return None

def detect_language(text: str) -> str:
    try: return detect_lang(text)
    except Exception: return "en"

def pick_voice_for_emotion(emotion: str) -> str:
    return {"neutral":"alloy","empathetic":"aria","cheerful":"bright","calm":"sage","excited":"coral","serious":"verse","sad":"aria","angry":"verse"}.get(emotion,"alloy")

def emotion_tone_instruction(emotion: str, language_code: str) -> str:
    tone={"neutral":"Maintain a neutral, clear tone.","empathetic":"Adopt an empathetic and supportive tone.","cheerful":"Adopt a positive and cheerful tone.","calm":"Adopt a calm and reassuring tone.","excited":"Adopt an enthusiastic and upbeat tone.","serious":"Adopt a concise and serious tone.","sad":"Adopt a gentle and compassionate tone.","angry":"Stay calm and de-escalate; avoid confrontational language."}.get(emotion,"Maintain a neutral tone.")
    return f"Respond in language '{language_code}'. {tone}"
