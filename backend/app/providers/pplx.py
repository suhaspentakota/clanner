import httpx, time
from app.config import settings

def pplx_chat(messages, model=None, max_tokens=800, temperature=0.2):
    if not settings.PPLX_API_KEY:
        return None
    url="https://api.perplexity.ai/chat/completions"
    headers={"Authorization": f"Bearer {settings.PPLX_API_KEY}"}
    data={"model": model or settings.CLANNER_DEFAULT_PPLX_MODEL,"messages":messages,"max_tokens":max_tokens,"temperature":temperature}
    t0=time.time()
    resp=httpx.post(url,headers=headers,json=data,timeout=60)
    t1=time.time()
    resp.raise_for_status()
    content=resp.json()["choices"][0]["message"]["content"]
    return {"provider":"pplx","model":data["model"],"output":content,"latency_ms":int((t1-t0)*1000)}
