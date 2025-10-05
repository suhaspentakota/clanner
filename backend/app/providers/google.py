import httpx, time
from app.config import settings

def google_chat(messages, model=None, max_tokens=800, temperature=0.2):
    if not settings.GOOGLE_API_KEY:
        return None
    mdl=model or settings.CLANNER_DEFAULT_GOOGLE_MODEL
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={settings.GOOGLE_API_KEY}"
    parts=[]
    for m in messages:
        if m["role"] in ("user","assistant","system"):
            parts.append({"text": m["content"]})
    data={"contents":[{"role":"user","parts":parts}],"generationConfig":{"maxOutputTokens":max_tokens,"temperature":temperature}}
    t0=time.time()
    resp=httpx.post(url,json=data,timeout=60)
    t1=time.time()
    resp.raise_for_status()
    j=resp.json()
    c=j.get("candidates",[])
    content=c[0]["content"]["parts"][0]["text"] if c else ""
    return {"provider":"google","model":mdl,"output":content,"latency_ms":int((t1-t0)*1000)}
