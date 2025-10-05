from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Tuple, Callable, Dict, Any
from app.providers import openai, anthropic, google, pplx, search, rag
from app.providers import groq, mistral, together, openrouter, azure_openai
from app.config import settings
import time

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None
    mode: str = "auto"  # openai | anthropic | google | pplx | groq | mistral | together | openrouter | azure_openai | ensemble | mix_ai | auto
    model: Optional[str] = None
    search: bool = False
    retrieval: bool = False
    max_tokens: int = 800
    temperature: float = 0.2

class ChatResponse(BaseModel):
    output: str
    citations: Optional[list] = []
    provider_traces: Optional[list] = []

def available_providers() -> List[Tuple[str, Callable]]:
    provs=[]
    if settings.OPENAI_API_KEY: provs.append(("openai", openai.openai_chat))
    if settings.ANTHROPIC_API_KEY: provs.append(("anthropic", anthropic.anthropic_chat))
    if settings.GOOGLE_API_KEY: provs.append(("google", google.google_chat))
    if settings.GROQ_API_KEY: provs.append(("groq", groq.groq_chat))
    if settings.MISTRAL_API_KEY: provs.append(("mistral", mistral.mistral_chat))
    if settings.TOGETHER_API_KEY: provs.append(("together", together.together_chat))
    if settings.OPENROUTER_API_KEY: provs.append(("openrouter", openrouter.openrouter_chat))
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_DEPLOYMENT:
        provs.append(("azure_openai", azure_openai.azure_openai_chat))
    if settings.PPLX_API_KEY: provs.append(("pplx", pplx.pplx_chat))
    return provs

def first_available_judge() -> Optional[Tuple[str, Callable]]:
    provs = available_providers()
    return provs[0] if provs else None

def synthesize_best_answer(user_prompt: str, candidate_outputs: List[Dict[str, Any]], citations: List[Dict[str, str]], judge_model: Optional[str] = None, max_tokens: int = 800, temperature: float = 0.1) -> Optional[Dict[str, Any]]:
    judge = first_available_judge()
    if not judge: return None
    judge_name, judge_fn = judge
    sys=("You are Clanner Mix AI, a meta-ensemble judge. Combine multiple model answers into ONE best answer.\n"
         "Rules:\n- Prefer agreements; note disagreements briefly.\n- State uncertainty when needed.\n- Be concise and structured.\n- Use citations conceptually if provided, do not invent sources.")
    cand_text=[]
    for i,c in enumerate(candidate_outputs, start=1):
        snippet=(c["output"] or "").strip()
        if len(snippet)>8000: snippet=snippet[:8000]+"\n...[truncated]..."
        cand_text.append(f"{i}. [{c['provider']} · {c['model']}] {snippet}")
    cite_text=""
    if citations:
        cite_text="\nCitations:\n" + "\n".join(f"- {c['title']}: {c['url']}" for c in citations)
    judge_messages=[{"role":"system","content":sys},{"role":"user","content":f"User question:\n{user_prompt}\n\nCandidate answers:\n" + "\n\n".join(cand_text) + cite_text}]
    t0=time.time()
    out=judge_fn(judge_messages, model=judge_model, max_tokens=max_tokens, temperature=temperature)
    t1=time.time()
    if not out: return None
    return {"provider":"mix_ai","model":f"judge:{out['provider']}::{out['model']}","output":out["output"],"latency_ms":int((t1-t0)*1000)}

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    citations=[]
    messages=[m.model_dump() for m in req.messages]

    if req.retrieval:
        docs=rag.retrieve(messages[-1]["content"])
        if docs:
            messages.append({"role":"system","content":"Context:\n" + "\n\n".join(docs)})

    if req.search:
        citations=search.bing_search(messages[-1]["content"]) or []
        if citations:
            messages.append({"role":"system","content":"Use these citations when answering:\n" + "\n".join(f"- {c['title']}: {c['url']}" for c in citations)})

    def call(fn):
        return fn(messages, model=req.model, max_tokens=req.max_tokens, temperature=req.temperature)

    direct_map={"openai":openai.openai_chat,"anthropic":anthropic.anthropic_chat,"google":google.google_chat,"pplx":pplx.pplx_chat,"groq":groq.groq_chat,"mistral":mistral.mistral_chat,"together":together.together_chat,"openrouter":openrouter.openrouter_chat,"azure_openai":azure_openai.azure_openai_chat}
    if req.mode in direct_map:
        out=direct_map[req.mode](messages, model=req.model, max_tokens=req.max_tokens, temperature=req.temperature)
        if out is None:
            return ChatResponse(output=f"Provider {req.mode} not configured.", citations=citations, provider_traces=[])
        return ChatResponse(output=out["output"], citations=citations, provider_traces=[out])

    if req.mode == "ensemble":
        outs=[]
        for name,fn in available_providers():
            try:
                r=call(fn)
                if r: outs.append(r)
            except Exception:
                pass
        if not outs:
            return ChatResponse(output="No providers configured.", citations=citations, provider_traces=[])
        output="\n\n---\n\n".join([f"{o['provider'].capitalize()} ({o['model']}):\n{o['output']}" for o in outs])
        return ChatResponse(output=output, citations=citations, provider_traces=outs)

    if req.mode == "mix_ai":
        outs=[]
        for name,fn in available_providers():
            try:
                r=call(fn)
                if r: outs.append(r)
            except Exception:
                pass
        if not outs:
            return ChatResponse(output="No providers configured.", citations=citations, provider_traces=[])
        judge_trace=synthesize_best_answer(user_prompt=req.messages[-1].content if req.messages else "", candidate_outputs=outs, citations=citations, judge_model=None, max_tokens=req.max_tokens, temperature=0.1)
        if judge_trace is None:
            output="\n\n---\n\n".join([f"{o['provider'].capitalize()} ({o['model']}):\n{o['output']}" for o in outs])
            return ChatResponse(output=output, citations=citations, provider_traces=outs)
        return ChatResponse(output=judge_trace["output"], citations=citations, provider_traces=outs+[judge_trace])

    for name,fn in available_providers():
        try:
            out=call(fn)
            if out:
                return ChatResponse(output=out["output"], citations=citations, provider_traces=[out])
        except Exception:
            continue
    return ChatResponse(output="No providers configured.", citations=citations, provider_traces=[])
