import { useEffect, useMemo, useRef, useState } from 'react'
type VoiceChatResponse = { transcript: string; language: string; emotion: string; reply_text: string; audio_b64: string; audio_format: string; voice: string; citations?: { title: string; url: string }[]; provider_traces?: { provider: string; model: string; latency_ms: number }[] }
const API_BASE = (import.meta as any).env?.VITE_CLANNER_API_URL || 'http://localhost:8000/v1'
export default function VoiceCard() {
  const [recording, setRecording] = useState(false)
  const [mediaSupported, setMediaSupported] = useState(false)
  const [deviceError, setDeviceError] = useState<string | null>(null)
  const [resp, setResp] = useState<VoiceChatResponse | null>(null)
  const [mode, setMode] = useState('mix_ai')
  const [search, setSearch] = useState(false)
  const [retrieval, setRetrieval] = useState(false)
  const [hintLang, setHintLang] = useState('')
  const [busy, setBusy] = useState(false)
  const chunksRef = useRef<BlobPart[]>([])
  const recRef = useRef<MediaRecorder | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  useEffect(()=>{ setMediaSupported(!!(navigator.mediaDevices && (window as any).MediaRecorder)) },[])
  async function startRecording() {
    setDeviceError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
      chunksRef.current = []
      rec.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data) }
      rec.onstop = async () => { const blob = new Blob(chunksRef.current, { type: 'audio/webm' }); await sendVoice(blob); stream.getTracks().forEach(t => t.stop()) }
      recRef.current = rec; rec.start(); setRecording(true)
    } catch (e: any) { setDeviceError(e?.message || 'Microphone not available') }
  }
  function stopRecording(){ recRef.current?.stop(); setRecording(false) }
  async function sendVoice(blob: Blob){
    setBusy(true); setResp(null)
    try{
      const form=new FormData()
      form.append('audio', blob, 'audio.webm'); form.append('mode', mode); form.append('search', String(search)); form.append('retrieval', String(retrieval))
      if (hintLang.trim()) form.append('hint_language', hintLang.trim())
      const res=await fetch(`${API_BASE}/voice/chat`,{method:'POST',body:form})
      if(!res.ok) throw new Error(await res.text())
      const data: VoiceChatResponse = await res.json(); setResp(data)
      const b=atob(data.audio_b64); const bin=new Uint8Array(b.length); for(let i=0;i<b.length;i++) bin[i]=b.charCodeAt(i)
      const url=URL.createObjectURL(new Blob([bin],{type:'audio/mpeg'})); if(audioRef.current){ audioRef.current.src=url; audioRef.current.play().catch(()=>{}) }
    }catch(e:any){ setDeviceError(e?.message || 'Voice request failed') } finally{ setBusy(false) }
  }
  const emotionChip = useMemo(()=>{ if(!resp?.emotion) return null; const map:Record<string,string>={ empathetic:'#8BC34A', cheerful:'#FFC107', calm:'#80DEEA', excited:'#FF7043', serious:'#B0BEC5', sad:'#90A4AE', angry:'#EF5350', neutral:'#9FA8DA' }; const bg=map[resp.emotion]||'#9FA8DA'; return <span className="chip" style={{background:bg}}>{resp.emotion}</span> },[resp])
  return (
    <section className="card">
      <div className="card-header">
        <div className="card-title"><h2>Voice</h2><span className={`status ${busy ? 'busy' : 'idle'}`}>{busy ? 'Processing…' : 'Ready'}</span></div>
        <div className="card-controls">
          <div className="control"><label htmlFor="mode">Provider</label>
            <select id="mode" value={mode} onChange={e => setMode(e.target.value)}>
              <option value="mix_ai">Mix AI (Best)</option><option value="ensemble">Ensemble (All)</option><option value="auto">Auto</option>
              <option value="openai">OpenAI</option><option value="anthropic">Anthropic</option><option value="google">Google</option>
              <option value="pplx">Perplexity</option><option value="groq">Groq</option><option value="mistral">Mistral</option>
              <option value="together">Together</option><option value="openrouter">OpenRouter</option><option value="azure_openai">Azure OpenAI</option>
            </select>
          </div>
          <div className="toggle"><input id="search" type="checkbox" checked={search} onChange={e => setSearch(e.target.checked)} /><label htmlFor="search">Web search</label></div>
          <div className="toggle"><input id="retrieval" type="checkbox" checked={retrieval} onChange={e => setRetrieval(e.target.checked)} /><label htmlFor="retrieval">Retrieval</label></div>
          <div className="control"><label htmlFor="hint">Hint language (e.g., es, fr, hi)</label><input id="hint" className="input" placeholder="auto" value={hintLang} onChange={e => setHintLang(e.target.value)} style={{ minWidth: 160 }} /></div>
        </div>
      </div>
      <div className="card-body">
        {!mediaSupported && <div className="alert error">This browser does not support microphone recording (MediaRecorder).</div>}
        <div className="voice-controls"><button className={`btn ${recording ? 'secondary' : 'primary'}`} disabled={!mediaSupported || busy} onClick={recording ? stopRecording : startRecording}>{recording ? 'Stop' : 'Record'}</button><audio ref={audioRef} controls style={{ width: '100%' }} /></div>
        {deviceError && <div className="alert error">⚠️ {deviceError}</div>}
        {resp && (
          <div className="voice-result">
            <div className="section-title">Transcript ({resp.language})</div>
            <div className="bubble-row right"><div className="bubble user"><div className="bubble-content"><p>{resp.transcript}</p></div><div className="avatar">🙂</div></div></div>
            <div className="section-title">Assistant {emotionChip}</div>
            <div className="bubble-row left"><div className="bubble assistant"><div className="avatar">🧠</div><div className="bubble-content"><p>{resp.reply_text}</p></div></div></div>
            {resp.citations?.length ? (<div className="citations"><div className="section-title">Citations</div><ul>{resp.citations.map((c,i)=><li key={i}><a href={c.url} target="_blank" rel="noreferrer">{c.title}</a></li>)}</ul></div>) : null}
            {resp.provider_traces?.length ? (<div className="providers"><div className="section-title">Providers</div><div className="provider-grid">{resp.provider_traces.map((p,i)=>(<div className="provider-chip" key={i} title={`${p.model}`}><span className="dot" /><span className="name">{p.provider}</span><span className="meta">{p.latency_ms} ms</span></div>))}</div></div>) : null}
          </div>
        )}
      </div>
    </section>
  )
}
