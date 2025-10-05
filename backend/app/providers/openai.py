import httpx, time
from app.config import settings

def openai_chat(messages, model=None, max_tokens=800, temperature=0.2):
    if not settings.OPENAI_API_KEY:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    data = {"model": model or settings.CLANNER_DEFAULT_OPENAI_MODEL,"messages": messages,"max_tokens": max_tokens,"temperature": temperature}
    t0 = time.time()
    resp = httpx.post(url, headers=headers, json=data, timeout=60)
    t1 = time.time()
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return {"provider":"openai","model":data["model"],"output":content,"latency_ms":int((t1-t0)*1000)}

def openai_embed(texts, model=None):
    url = "https://api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    data = {"model": model or settings.CLANNER_EMBEDDING_MODEL, "input": texts}
    resp = httpx.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return [d["embedding"] for d in resp.json()["data"]]
