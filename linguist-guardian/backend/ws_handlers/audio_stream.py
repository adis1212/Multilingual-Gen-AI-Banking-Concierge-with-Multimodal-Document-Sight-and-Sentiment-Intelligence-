from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.whisper_client import transcribe_audio
from core.gpt4o_client import extract_intent
from core.sentiment_engine import analyze_audio_sentiment
import json, uuid

router = APIRouter()

# Active sessions store
active_sessions: dict[str, dict] = {}


@router.websocket("/audio/{session_id}")
async def audio_websocket(websocket: WebSocket, session_id: str):
    """
    Real-time dual-channel audio stream handler.
    Client sends: { channel: "A"|"B", language: "mr", audio_chunk: <base64> }
    Server sends: transcription + intent + sentiment in real-time
    """
    await websocket.accept()
    active_sessions[session_id] = {"customer_ctx": {}}
    print(f"WS connected: session {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            channel  = payload.get("channel", "A")
            language = payload.get("language", "mr")
            audio_b64 = payload.get("audio_chunk", "")

            if not audio_b64:
                continue

            import base64
            audio_bytes = base64.b64decode(audio_b64)

            # 1. Transcribe
            transcript = await transcribe_audio(audio_bytes, language, channel)

            result = {"type": "transcript", "channel": channel, **transcript}

            # 2. If customer channel — extract intent + sentiment
            if channel == "A" and transcript.get("text"):
                intent, sentiment = await _parallel_analyze(
                    transcript["text"],
                    language,
                    audio_bytes,
                    active_sessions[session_id]["customer_ctx"]
                )
                result["intent"] = intent
                result["sentiment"] = sentiment

                # Update session context
                active_sessions[session_id]["customer_ctx"] = {
                    "last_intent": intent.get("intent"),
                    "emotion": sentiment.get("emotion"),
                }

            await websocket.send_text(json.dumps(result))

    except WebSocketDisconnect:
        active_sessions.pop(session_id, None)
        print(f"WS disconnected: session {session_id}")
    except Exception as e:
        print(f"WS error: {e}")
        await websocket.close()


async def _parallel_analyze(text, language, audio_bytes, ctx):
    import asyncio
    intent_task   = extract_intent(text, language, ctx)
    sentiment_task = analyze_audio_sentiment(audio_bytes)
    intent, sentiment = await asyncio.gather(intent_task, sentiment_task)
    return intent, {
        "stress_level": sentiment.stress_level,
        "emotion": sentiment.emotion,
        "deescalate": sentiment.deescalate,
        "tips": sentiment.tips,
    }