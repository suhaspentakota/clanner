from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.chat import router as chat_router
from app.routers.voice import router as voice_router

app = FastAPI(title="Clanner API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/v1")
app.include_router(voice_router, prefix="/v1")

@app.get("/")
def root():
    return {"ok": True, "name": "Clanner", "version": "0.2.0"}
