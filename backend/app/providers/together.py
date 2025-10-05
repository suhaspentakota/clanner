import httpx, time
from app.config import settings

def together_chat(messages, model=None, max_tokens=800, temperature=0.2):
    if not settings.TOGETHER_API_KEY:
        return None
    url="https://api.together.xyz/v1/chat/completions"
    headers={"Authorization": f"Bearer {settings.TOGETHER_API_KEY}","Content-Type":"application/json"}
    data={"model": model or settings.CLANNER_DEFAULT_TOGETHER_MODEL,"messages":messages,"max_tokens":max_tokens,"temperature":temperature}
    t0=time.time()
    resp=httpx.post(url,headers=headers,json=data,timeout=60)
    t1=time.time()
    resp.raise_for_status()
    j=resp.json()
    content=j["choices"][0]["message"]["content"]
    return {"provider":"together","model":data["model"],"output":content,"latency_ms":int((t1-t0)*1000)}
