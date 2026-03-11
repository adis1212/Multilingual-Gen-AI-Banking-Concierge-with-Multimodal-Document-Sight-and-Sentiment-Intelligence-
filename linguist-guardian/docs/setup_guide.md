# 🚀 Linguist-Guardian — Setup Guide

## Prerequisites

- **Python 3.10+** (backend)
- **Node.js 18+** (frontend)
- **API Keys**: OpenAI, ElevenLabs, Sarvam AI

---

## Quick Setup (Windows)

### 1. Backend

```powershell
cd linguist-guardian/backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Edit .env and replace placeholder values with your actual keys:
#   OPENAI_API_KEY=sk-your-key
#   ELEVENLABS_API_KEY=your-key
#   SARVAM_API_KEY=your-key

# Start server
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```powershell
cd linguist-guardian/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 3. Open Dashboard

Visit **http://localhost:3000** in your browser.

---

## Docker Setup (Optional)

```bash
cd linguist-guardian

# Edit backend/.env with your API keys first, then:
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for Whisper + GPT-4o |
| `ELEVENLABS_API_KEY` | ✅ | ElevenLabs TTS API key |
| `SARVAM_API_KEY` | ✅ | Sarvam AI API key for Indian languages |
| `DATABASE_URL` | ❌ | Default: `sqlite:///./linguist.db` |
| `SECRET_KEY` | ❌ | Session security key |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend REST API URL |
| `VITE_WS_URL` | `ws://localhost:8000` | Backend WebSocket URL |

---

## API Testing

```bash
# Health check
curl http://localhost:8000/health

# Extract intent
curl -X POST http://localhost:8000/api/intent/extract \
  -H "Content-Type: application/json" \
  -d '{"transcript": "I lost my card", "language": "en"}'

# Get TTS languages
curl http://localhost:8000/api/tts/languages
```

---

## Running Tests

```bash
# Backend tests
cd backend
python -m pytest ../tests/backend/ -v

# Frontend tests (if vitest configured)
cd frontend
npx vitest run ../tests/frontend/
```
