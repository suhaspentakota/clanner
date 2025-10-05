# Clanner — Personal AI Assistant (Multi‑Model, RAG, Search, Voice, Android)

Clanner blends the strengths of multiple models (OpenAI, Anthropic, Google Gemini, Perplexity, Groq, Mistral, Together, OpenRouter, Azure OpenAI) with:

- Routing and Ensemble modes
- Mix AI (Best): combines all provider answers into one best response
- RAG (local Chroma vector DB)
- Web search (Bing) with citations
- Multilingual Voice: talk + listen + respond in any language
- Artificial feelings: affect-aware responses and voice
- Web UI (React + Vite), CLI (Typer), Android app (Jetpack Compose)

Quick start
- Backend: Python 3.11+
  - cd backend && python -m venv .venv && source .venv/bin/activate
  - pip install -r requirements.txt
  - uvicorn app.main:app --reload --port 8000
- UI: Node 18+
  - cd frontend && npm install && npm run dev (http://localhost:5173)
- Android: Open android/ in Android Studio; the app uses http://10.0.2.2:8000/v1 to reach your local backend.

Environment (.env)
- Copy .env.example to .env and fill keys you have (OpenAI, Anthropic, Google, etc.).

ZIP download (after you push)
- Main branch ZIP: https://github.com/suhaspentakota/clanner/archive/refs/heads/main.zip

License: MIT
