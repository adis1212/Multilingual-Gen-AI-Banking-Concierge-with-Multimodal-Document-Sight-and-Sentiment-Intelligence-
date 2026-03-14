from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import transcription, intent, tts, ocr, sentiment, session, orchestrate
from ws_handlers.audio_stream import router as ws_router
from database.db import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    print("✅ Linguist-Guardian backend started")
    yield
    # Shutdown
    print("🛑 Shutting down")


app = FastAPI(
    title="Linguist-Guardian API",
    version="1.0.0",
    description="Multilingual AI Banking Concierge",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routes
app.include_router(transcription.router, prefix="/api/transcribe", tags=["Transcription"])
app.include_router(intent.router,        prefix="/api/intent",     tags=["Intent"])
app.include_router(tts.router,           prefix="/api/tts",        tags=["TTS"])
app.include_router(ocr.router,           prefix="/api/ocr",        tags=["OCR"])
app.include_router(sentiment.router,     prefix="/api/sentiment",  tags=["Sentiment"])
app.include_router(session.router,       prefix="/api/session",    tags=["Session"])
app.include_router(orchestrate.router,   prefix="/api/orchestrate", tags=["Orchestrator"])

# WebSocket
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "linguist-guardian"}