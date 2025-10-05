export type ChatMessage = { role: 'system' | 'user' | 'assistant'; content: string }
export type Citation = { title: string; url: string }
export type ProviderTrace = { provider: string; model: string; latency_ms: number }
export type ChatPayload = { messages: ChatMessage[]; session_id?: string; mode: 'auto'|'mix_ai'|'ensemble'|'openai'|'anthropic'|'google'|'pplx'|'groq'|'mistral'|'together'|'openrouter'|'azure_openai'; model?: string; search?: boolean; retrieval?: boolean; max_tokens?: number; temperature?: number }
export type ChatResponse = { output: string; citations?: Citation[]; provider_traces?: ProviderTrace[] }
