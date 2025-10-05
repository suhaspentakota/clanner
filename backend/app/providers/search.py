import httpx
from app.config import settings

def bing_search(query):
    if not settings.BING_SUBSCRIPTION_KEY:
        return None
    url="https://api.bing.microsoft.com/v7.0/search"
    headers={"Ocp-Apim-Subscription-Key": settings.BING_SUBSCRIPTION_KEY}
    params={"q": query,"mkt":"en-US"}
    resp=httpx.get(url,headers=headers,params=params,timeout=20)
    resp.raise_for_status()
    results=resp.json()
    citations=[]
    if "webPages" in results:
        for r in results["webPages"]["value"][:5]:
            citations.append({"title": r["name"], "url": r["url"]})
    return citations
