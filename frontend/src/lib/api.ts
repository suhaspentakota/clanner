import { ChatPayload, ChatResponse } from '../types'
const BASE_URL = (import.meta as any).env?.VITE_CLANNER_API_URL || 'http://localhost:8000/v1'
export async function sendChat(payload: ChatPayload): Promise<ChatResponse> {
  const res = await fetch(`${BASE_URL}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
