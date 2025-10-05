import { useState } from 'react'
import ChatCard from './components/ChatCard'
import VoiceCard from './components/VoiceCard'

export default function App() {
  const [tab, setTab] = useState<'chat' | 'voice'>('chat')
  return (
    <div className="page">
      <header className="header">
        <div className="brand">
          <div className="logo">🧠</div>
          <div className="title">
            <h1>Clanner</h1>
            <p className="subtitle">Your multi-model AI assistant</p>
          </div>
        </div>
        <nav className="tabs">
          <button className={`tab ${tab==='chat'?'active':''}`} onClick={() => setTab('chat')}>Chat</button>
          <button className={`tab ${tab==='voice'?'active':''}`} onClick={() => setTab('voice')}>Voice</button>
        </nav>
      </header>
      <main className="container">
        {tab === 'chat' ? <ChatCard /> : <VoiceCard />}
      </main>
      <footer className="footer"><span>Made with ❤️ for multi-model orchestration</span></footer>
    </div>
  )
}
