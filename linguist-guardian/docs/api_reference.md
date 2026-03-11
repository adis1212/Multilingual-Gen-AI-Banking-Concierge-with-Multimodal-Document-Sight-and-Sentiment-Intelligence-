# 📘 Linguist-Guardian API Reference

## Base URL
```
http://localhost:8000
```

---

## Health Check

### `GET /health`
```json
{ "status": "ok", "service": "linguist-guardian" }
```

---

## Transcription

### `POST /api/transcribe/`
Transcribe full audio file using Whisper.

**Body** (multipart/form-data):
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `audio` | File | required | Audio file (.webm, .wav, .ogg, .mpeg) |
| `language` | string | `"mr"` | ISO language code |
| `channel` | string | `"A"` | `"A"` = customer, `"B"` = staff |

**Response**:
```json
{
  "text": "मला माझे कार्ड हरवले आहे",
  "language": "mr",
  "channel": "A",
  "words": [{"word": "मला", "start": 0.0, "end": 0.5}],
  "duration": 3.5,
  "translation": "I lost my card"
}
```

### `POST /api/transcribe/stream-chunk`
Same as above but includes `session_id` field.

---

## Intent Extraction

### `POST /api/intent/extract`
Extract customer intent from transcript using GPT-4o.

**Body** (JSON):
```json
{
  "transcript": "मला माझे कार्ड हरवले आहे",
  "language": "mr",
  "customer_context": {},
  "session_id": "sess-001"
}
```

**Response**:
```json
{
  "intent": "lost_card",
  "urgency": "critical",
  "emotion": "distressed",
  "stress_keywords": ["हरवले"],
  "staff_advisory": "Initiate card block immediately.",
  "suggested_actions": ["block_card", "reissue_card"],
  "banking_processes": ["CARD_BLOCK", "CARD_REISSUE"],
  "response_in_customer_language": "काळजी करू नका...",
  "escalate_to_manager": false
}
```

### `POST /api/intent/compliance`
Silent RBI compliance check on staff utterance.

**Body** (JSON):
```json
{
  "staff_utterance": "You should buy our premium insurance plan.",
  "session_id": "sess-001"
}
```

**Response**:
```json
{
  "compliant": false,
  "violations": ["Did not disclose insurance is not a bank product"],
  "warning_message": "Staff must inform...",
  "severity": "high"
}
```

---

## Text-to-Speech

### `POST /api/tts/synthesize`
Convert text to speech (returns audio/mpeg).

**Body** (JSON):
```json
{
  "text": "काळजी करू नका, प्रिया जी.",
  "language": "mr",
  "emotion": "neutral",
  "provider": "elevenlabs"
}
```

### `GET /api/tts/languages`
Returns list of supported TTS languages with available providers.

---

## Document Analysis (OCR)

### `POST /api/ocr/analyze`
Analyze document image with GPT-4o Vision.

**Body** (multipart/form-data):
| Field | Type | Description |
|-------|------|-------------|
| `image` | File | JPEG/PNG/WEBP image |
| `doc_type` | string | `aadhaar`, `pan`, `passbook`, `utility_bill` |
| `customer_record` | string | JSON string of customer data |

**Response**:
```json
{
  "doc_type": "aadhaar",
  "extracted_fields": {"name": "Priya Sharma", "dob": "12/03/1990"},
  "cross_check_results": [{"field": "name", "status": "match"}],
  "ocr_confidence": 0.97,
  "verification_status": "partial",
  "staff_action": "Request utility bill for address verification."
}
```

---

## Sentiment Analysis

### `POST /api/sentiment/analyze`
Analyze emotional state from audio.

**Body** (multipart/form-data):
| Field | Type | Description |
|-------|------|-------------|
| `audio` | File | Audio file |

**Response**:
```json
{
  "stress_level": 0.78,
  "pitch_rise_pct": 22.0,
  "speech_rate": "fast",
  "volume": "medium",
  "emotion": "distressed",
  "deescalate": true,
  "tips": ["Offer complimentary refreshment", "Use a slower tone"]
}
```

---

## Session Management

### `POST /api/session/create`
### `GET /api/session/{session_id}`
### `POST /api/session/close`
### `POST /api/session/{session_id}/action`
### `GET /api/session/branch/{branch_id}`

---

## WebSocket

### `WS /ws/audio/{session_id}`

**Client sends**:
```json
{ "channel": "A", "language": "mr", "audio_chunk": "<base64>" }
```

**Server sends**:
```json
{
  "type": "transcript",
  "channel": "A",
  "text": "...",
  "intent": { ... },
  "sentiment": { "stress_level": 0.78, "emotion": "distressed", ... }
}
```
