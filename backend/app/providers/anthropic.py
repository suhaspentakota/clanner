import httpx, time
from app.config import settings

def anthropic_chat(messages, model=None, max_tokens=800, temperature=0.2):
    if not settings.ANTHROPIC_API_KEY:
        return None
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": settings.ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}
    system = None
    mm=[]
    for m in messages:
        if m["role"]=="system": system=m["content"]
        elif m["role"]=="user": mm.append({"role":"user","content":m["content"]})
        elif m["role"]=="assistant": mm.append({"role":"assistant","content":m["content"]})
    data={"model": model or settings.CLANNER_DEFAULT_ANTHROPIC_MODEL,"max_tokens":max_tokens,"temperature":temperature,"messages":mm}
    if system: data["system"]=system
    t0=time.time()
    resp=httpx.post(url,headers=headers,json=data,timeout=60)
    t1=time.time()
    resp.raise_for_status()
    content=resp.json()["content"][0]["text"]
    return {"provider":"anthropic","model":data["model"],"output":content,"latency_ms":int((t1-t0)*1000)}
