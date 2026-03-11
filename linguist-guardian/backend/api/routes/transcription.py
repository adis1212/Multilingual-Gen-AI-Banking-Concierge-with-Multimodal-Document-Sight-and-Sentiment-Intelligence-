from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from core.whisper_client import transcribe_audio, translate_to_english

router = APIRouter()


@router.post("/")
async def transcribe(
    audio: UploadFile = File(...),
    language: str = Form("mr"),
    channel: str = Form("A"),
):
    """Transcribe uploaded audio file."""
    if audio.content_type not in ["audio/webm", "audio/wav", "audio/mpeg", "audio/ogg"]:
        raise HTTPException(400, "Unsupported audio format")

    audio_bytes = await audio.read()
    result = await transcribe_audio(audio_bytes, language, channel)

    if "error" in result:
        raise HTTPException(500, result["error"])

    # Auto-translate to English for staff display
    if language != "en" and result.get("text"):
        result["translation"] = await translate_to_english(result["text"], language)

    return result


@router.post("/stream-chunk")
async def transcribe_chunk(
    audio: UploadFile = File(...),
    language: str = Form("mr"),
    channel: str = Form("A"),
    session_id: str = Form(...),
):
    """Transcribe a streaming audio chunk (called every ~3 seconds)."""
    audio_bytes = await audio.read()
    result = await transcribe_audio(audio_bytes, language, channel)

    if language != "en" and result.get("text"):
        result["translation"] = await translate_to_english(result["text"], language)

    result["session_id"] = session_id
    return result