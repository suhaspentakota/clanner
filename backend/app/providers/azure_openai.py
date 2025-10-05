import httpx, time
from app.config import settings

def azure_openai_chat(messages, model=None, max_tokens=800, temperature=0.2):
    if not (settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_DEPLOYMENT):
        return None
    base=settings.AZURE_OPENAI_ENDPOINT.rstrip("/")
    api_version=settings.AZURE_OPENAI_API_VERSION or "2024-06-01"
    url=f"{base}/openai/deployments/{settings.AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={api_version}"
    headers={"api-key": settings.AZURE_OPENAI_API_KEY,"Content-Type":"application/json"}
    data={"messages":messages,"max_tokens":max_tokens,"temperature":temperature}
    t0=time.time()
    resp=httpx.post(url,headers=headers,json=data,timeout=60)
    t1=time.time()
    resp.raise_for_status()
    j=resp.json()
    content=j["choices"][0]["message"]["content"]
    return {"provider":"azure_openai","model":settings.AZURE_OPENAI_DEPLOYMENT,"output":content,"latency_ms":int((t1-t0)*1000)}
