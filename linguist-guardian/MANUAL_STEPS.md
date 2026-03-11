# 📋 Manual Steps & Remaining Tasks

> These are tasks that require **human input** or **external resources** that cannot be automated.

---

## 🔑 1. API Keys (YOU MUST DO THIS)

### OpenAI API Key
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Paste into `backend/.env` → `OPENAI_API_KEY=sk-proj-...`
4. **Required for**: Whisper STT, GPT-4o intent, GPT-4o Vision OCR, compliance, summaries

### ElevenLabs API Key
1. Go to [elevenlabs.io](https://elevenlabs.io) → Profile → API Key
2. Paste into `backend/.env` → `ELEVENLABS_API_KEY=sk_...`
3. **Required for**: English/multilingual TTS
4. **Optional**: Create custom Indian-accent voices and update voice IDs in `core/elevenlabs_client.py`

### Sarvam AI API Key
1. Go to [sarvam.ai](https://www.sarvam.ai) → Dashboard → API Keys
2. Paste into `backend/.env` → `SARVAM_API_KEY=sk_...`
3. **Required for**: Indian language STT/TTS (better accent than ElevenLabs for Indian languages)

---

## 🗃️ 2. Database Seeding (Recommended)

Run the seed script to populate demo customer data and RBI guidelines:

```powershell
cd linguist-guardian/backend
C:\tmp\lg-venv\Scripts\python.exe -m database.seed
```

This creates:
- 3 demo customers (Priya Sharma, Ramesh Patil, Kavitha Suresh)
- 6 RBI guideline entries in ChromaDB for RAG

---

## 🎙️ 3. ElevenLabs Voice Configuration (Optional)

For premium Indian-accented voices:
1. Go to ElevenLabs → Voice Library
2. Find/create voices for Hindi, Marathi, Tamil, etc.
3. Copy voice IDs and update `VOICE_MAP` in `backend/core/elevenlabs_client.py`:

```python
VOICE_MAP = {
    "mr": "your-marathi-voice-id",
    "hi": "your-hindi-voice-id",
    ...
}
```

If you skip this, the system uses the default "Rachel" voice (English).

---

## 🐳 4. Docker / Production Setup (Optional)

### PostgreSQL (for production)
1. Update `DATABASE_URL` in `backend/.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/linguist
   ```
2. Install `asyncpg`: `pip install asyncpg`
3. Or use `docker-compose up` which includes PostgreSQL automatically

### Deploy to Cloud
1. Set all env vars in your cloud provider
2. Use `docker-compose.yml` for container orchestration
3. Configure SSL/TLS for WebSocket connections

---

## 🧪 5. Run Tests (Optional)

```powershell
# Backend (mocked, no API keys needed)
cd linguist-guardian/backend
C:\tmp\lg-venv\Scripts\python.exe -m pytest ../tests/backend/ -v

# E2E (needs backend running)
cd linguist-guardian
npx jest tests/e2e/full_session.test.js

# Frontend (needs vitest)
cd linguist-guardian/frontend
npx vitest run ../tests/frontend/
```

---

## 🔒 6. Security Hardening (Before Production)

- [ ] Change `SECRET_KEY` in `backend/.env` to a random 64-char string
- [ ] Enable JWT auth by activating token validation in `api/middleware/auth.py`
- [ ] Set up HTTPS/WSS for WebSocket connections
- [ ] Remove demo data from `database/seed.py`
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Add rate limiting redis backend (replace in-memory `rateLimit.py`)

---

## 📊 7. RAG Enrichment (Optional)

To add more RBI guidelines to the vector store:
1. Prepare documents as a list of dicts: `[{"id": "...", "text": "...", "source": "...", "category": "..."}]`
2. Call `from rag.vector_store import ingest_documents; ingest_documents(docs)`
3. Or add them to `database/seed.py` → `RBI_GUIDELINES` list and re-run seed

---

## ✅ Project Completion Checklist

### Fully Automated (Done)
- [x] All backend core AI clients (5 files)
- [x] All API routes (6 endpoints)
- [x] WebSocket audio streaming
- [x] Database models + seed data
- [x] RAG pipeline (ChromaDB + embeddings)
- [x] ML modules (dialect detector, intent classifier, keyword spotter)
- [x] All frontend pages (3)
- [x] All frontend components (12)
- [x] All frontend hooks (4)
- [x] All frontend services (4)
- [x] All frontend utils (3)
- [x] All frontend stores (3)
- [x] All tests (5 files)
- [x] All documentation (3 files)

### Manual Steps (Your Responsibility)
- [ ] Add actual API keys to `backend/.env`
- [ ] Run database seed: `python -m database.seed`
- [ ] (Optional) Configure ElevenLabs voice IDs
- [ ] (Optional) Add more RBI guidelines to RAG
- [ ] (Optional) Security hardening for production
