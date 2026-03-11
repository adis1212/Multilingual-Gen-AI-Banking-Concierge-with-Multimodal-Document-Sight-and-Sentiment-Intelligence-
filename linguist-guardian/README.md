# 🛡️ Linguist-Guardian

### Multilingual Gen-AI Banking Concierge with Multimodal Document Sight & Sentiment Intelligence

A real-time AI concierge system for Indian bank branches. It listens to customer-staff conversations in regional languages, transcribes and translates in real-time, extracts intent, monitors emotional state, verifies documents via camera, and ensures RBI compliance — all on a single staff dashboard.

---

## ✨ Features

| Feature | Technology | What It Does |
|---------|------------|-------------|
| **Speech-to-Text** | OpenAI Whisper + Sarvam AI | Real-time transcription of 9 Indian languages |
| **AI Intent Engine** | GPT-4o | Extracts customer intent, urgency, and recommended staff actions |
| **Document Sight** | GPT-4o Vision | OCR + auto-verification of Aadhaar, PAN, Passbook against records |
| **Sentiment Intelligence** | Librosa | Monitors pitch, speech rate, stress level — triggers de-escalation |
| **Text-to-Speech** | ElevenLabs + Sarvam | Emotion-adaptive voice responses in customer's language |
| **Compliance Whisper** | GPT-4o + RAG | Silent RBI compliance monitoring of staff utterances |
| **RAG Pipeline** | ChromaDB + SentenceTransformer | Retrieves relevant RBI guidelines during conversations |

## 🌐 Languages Supported

Marathi · Hindi · Tamil · Telugu · Bengali · Gujarati · Kannada · Malayalam · English

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- API Keys: [OpenAI](https://platform.openai.com), [ElevenLabs](https://elevenlabs.io), [Sarvam AI](https://sarvam.ai)

### 1. Backend Setup
```powershell
cd linguist-guardian/backend

# Create virtual environment (use short path to avoid Windows long-path issues)
python -m venv C:\tmp\lg-venv
C:\tmp\lg-venv\Scripts\python.exe -m pip install --upgrade pip
C:\tmp\lg-venv\Scripts\pip install -r requirements.txt

# Add your API keys
# Edit .env with your actual keys for OPENAI_API_KEY, ELEVENLABS_API_KEY, SARVAM_API_KEY

# Seed demo data (optional)
C:\tmp\lg-venv\Scripts\python.exe -m database.seed

# Start server
C:\tmp\lg-venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```powershell
cd linguist-guardian/frontend
npm install
node .\node_modules\vite\bin\vite.js --port 3000
```

### 3. Open Dashboard
Visit **http://localhost:3000** in your browser.

---

## 🏗️ Architecture

```
├── backend/
│   ├── main.py                  # FastAPI app + CORS + routers
│   ├── core/                    # AI service clients
│   │   ├── whisper_client.py    # Whisper STT
│   │   ├── gpt4o_client.py      # GPT-4o intent/compliance/OCR
│   │   ├── elevenlabs_client.py # ElevenLabs TTS
│   │   ├── sarvam_client.py     # Sarvam AI STT/TTS
│   │   └── sentiment_engine.py  # Librosa audio analysis
│   ├── api/routes/              # REST API endpoints
│   ├── ws_handlers/             # WebSocket real-time audio
│   ├── rag/                     # ChromaDB + embeddings
│   ├── database/                # SQLAlchemy + seed data
│   ├── models/                  # ORM models
│   ├── prompts/                 # GPT-4o system prompts
│   └── ml/                      # Dialect + intent + keyword ML
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, Reports, Session Detail
│   │   ├── components/          # UI components
│   │   ├── hooks/               # WebSocket, Audio, OCR, Sentiment
│   │   ├── store/               # Zustand state management
│   │   ├── services/            # API client wrappers
│   │   └── utils/               # Banking glossary, currency, language detect
│   └── vite.config.js
├── tests/                       # Backend, frontend, E2E tests
├── docs/                        # Architecture, API reference, setup guide
└── docker-compose.yml           # Backend + Frontend + PostgreSQL
```

---

## 📡 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/transcribe/` | Whisper audio transcription |
| `POST` | `/api/intent/extract` | GPT-4o intent extraction |
| `POST` | `/api/intent/compliance` | RBI compliance check |
| `POST` | `/api/tts/synthesize` | Text-to-speech |
| `POST` | `/api/ocr/analyze` | Document analysis (GPT-4o Vision) |
| `POST` | `/api/sentiment/analyze` | Audio sentiment analysis |
| `WS`   | `/ws/audio/{session_id}` | Real-time dual-channel audio |

Full API documentation: [docs/api_reference.md](docs/api_reference.md)

---

## 🧪 Testing

```bash
# Backend unit tests
C:\tmp\lg-venv\Scripts\python.exe -m pytest tests/backend/ -v

# E2E tests (requires backend running)
npx jest tests/e2e/full_session.test.js

# Frontend component tests
npx vitest run tests/frontend/
```

---

## 🐳 Docker

```bash
docker-compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

---

## 📚 Documentation

- [Architecture](docs/architecture.md) — System design with Mermaid diagram
- [API Reference](docs/api_reference.md) — All endpoints
- [Setup Guide](docs/setup_guide.md) — Detailed setup instructions

---

## 🛡️ Tech Stack

| Layer | Technology |
|-------|------------|
| STT | OpenAI Whisper Large-v3 + Sarvam AI Saarika v2 |
| Brain | GPT-4o (intent + compliance + summaries) |
| OCR | GPT-4o Vision |
| TTS | ElevenLabs Multilingual v2 + Sarvam Bulbul v1 |
| Sentiment | Librosa (pitch, speech rate, volume) |
| RAG | ChromaDB + SentenceTransformer (MiniLM-L6-v2) |
| Frontend | React 18 + Vite + Tailwind CSS + Zustand + Recharts |
| Backend | FastAPI + SQLAlchemy (async) + WebSockets |
| Database | SQLite (dev) / PostgreSQL (prod) |