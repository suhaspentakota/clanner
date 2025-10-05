type Props = { role: 'user' | 'assistant'; content: string }
export default function MessageBubble({ role, content }: Props) {
  const isUser = role === 'user'
  return (
    <div className={`bubble-row ${isUser ? 'right' : 'left'}`}>
      <div className={`bubble ${isUser ? 'user' : 'assistant'}`}>
        {!isUser && <div className="avatar">🧠</div>}
        <div className="bubble-content">{content.split('\n').map((l,i)=><p key={i}>{l}</p>)}</div>
        {isUser && <div className="avatar">🙂</div>}
      </div>
    </div>
  )
}
