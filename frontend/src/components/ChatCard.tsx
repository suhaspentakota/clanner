import { useMemo, useState } from 'react'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import { ChatMessage, ChatPayload, ChatResponse } from '../types'
import { sendChat } from '../lib/api'

const DEFAULT_SYSTEM = 'You are Clanner, a helpful, concise assistant.'
const PROVIDER_OPTIONS = [
  { value: 'auto', label: 'Auto' },
  { value: 'mix_ai', label: 'Mix AI (Best)' },
  { value: 'ensemble', label: 'Ensemble (All)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google' },
  { value: 'pplx', label: 'Perplexity' },
  { value: 'groq', label: 'Groq' },
  { value: 'mistral', label: 'Mistral' },
  { value: 'together', label: 'Together AI' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'azure_openai', label: 'Azure OpenAI' }
]

export default function ChatCard() {
  const [messages, setMessages] = useState<ChatMessage[]>([{ role: 'system', content: DEFAULT_SYSTEM }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<ChatPayload['mode']>('mix_ai')
  const [model, setModel] = useState<string>('')
  const [search, setSearch] = useState(false)
  const [retrieval, setRetrieval] = useState(false)
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const visibleMessages = useMemo(() => messages.filter(m => m.role !== 'system'), [messages])

  async function onSend(text?: string) {
    const prompt = (text ?? input).trim()
    if (!prompt || loading) return
    const newMessages = [...messages, { role: 'user', content: prompt } as ChatMessage]
    setMessages(newMessages); setInput(''); setLoading(true); setError(null)
    try {
      const payload: ChatPayload = { messages: newMessages, mode, search, retrieval, model: model.trim() || undefined }
      const resp = await sendChat(payload)
      setLastResponse(resp)
      setMessages(prev => [...prev, { role: 'assistant', content: resp.output }])
    } catch (e: any) { setError(e?.message || 'Request failed') } finally { setLoading(false) }
  }
  function resetChat() { setMessages([{ role: 'system', content: DEFAULT_SYSTEM }]); setLastResponse(null); setError(null) }

  return (
    <section className="card">
      <div className="card-header">
        <div className="card-title"><h2>Chat</h2><span className={`status ${loading ? 'busy' : 'idle'}`}>{loading ? 'Thinking…' : 'Ready'}</span></div>
        <div className="card-controls">
          <div className="control"><label htmlFor="mode">Provider</label>
            <select id="mode" value={mode} onChange={e => setMode(e.target.value as any)}>
              {PROVIDER_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          </div>
          <div className="control"><label htmlFor="model">Custom model (optional)</label>
            <input id="model" placeholder="e.g., gpt-5.0 | gemini-2.5-flash" value={model} onChange={e => setModel(e.target.value)} className="input" style={{ minWidth: 280 }} />
          </div>
          <div className="toggle"><input id="search" type="checkbox" checked={search} onChange={e => setSearch(e.target.checked)} /><label htmlFor="search">Web search</label></div>
          <div className="toggle"><input id="retrieval" type="checkbox" checked={retrieval} onChange={e => setRetrieval(e.target.checked)} /><label htmlFor="retrieval">Retrieval</label></div>
          <button className="btn secondary" onClick={resetChat} disabled={loading}>Reset</button>
        </div>
      </div>
      <div className="card-body">
        {visibleMessages.length===0 && <div className="empty"><p>Mix AI will consult all configured models and synthesize the best single answer.</p></div>}
        <div className="chat-area">{visibleMessages.map((m,i)=><MessageBubble key={i} role={m.role as any} content={m.content} />)}</div>
        {error && <div className="alert error"><span>⚠️ {error}</span></div>}
        {lastResponse?.citations?.length ? (<div className="citations"><div className="section-title">Citations</div><ul>{lastResponse.citations.map((c,idx)=><li key={idx}><a href={c.url} target="_blank" rel="noreferrer">{c.title}</a></li>)}</ul></div>):null}
        {lastResponse?.provider_traces?.length ? (<div className="providers"><div className="section-title">Providers</div><div className="provider-grid">{lastResponse.provider_traces.map((p,idx)=>(<div className="provider-chip" key={idx} title={`${p.model}`}><span className="dot" /><span className="name">{p.provider}</span><span className="meta">{p.latency_ms} ms</span></div>))}</div></div>):null}
      </div>
      <div className="card-footer"><MessageInput value={input} onChange={setInput} onSend={() => onSend()} disabled={loading} /></div>
    </section>
  )
}
