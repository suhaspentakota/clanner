import { useCallback } from 'react'
type Props = { value: string; onChange: (v: string) => void; onSend: () => void; disabled?: boolean }
export default function MessageInput({ value, onChange, onSend, disabled }: Props) {
  const onKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSend() }
  }, [onSend])
  return (
    <div className="input-row">
      <textarea className="input" placeholder="Type your message…" rows={1} value={value} onChange={e => onChange(e.target.value)} onKeyDown={onKeyDown} disabled={disabled} />
      <button className="btn primary" disabled={disabled || value.trim().length===0} onClick={onSend}>Send</button>
    </div>
  )
}
