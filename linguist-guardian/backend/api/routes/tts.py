from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from core.elevenlabs_client import synthesize_speech
from core.sarvam_client import synthesize_sarvam

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "mr"
    emotion: str = "neutral"
    provider: str = "elevenlabs"   # "elevenlabs" | "sarvam"


@router.post("/synthesize")
async def text_to_speech(req: TTSRequest):
    """Convert staff response text to customer's language audio."""
    if not req.text.strip():
        raise HTTPException(400, "Text is empty")

    try:
        if req.provider == "sarvam":
            audio_bytes = await synthesize_sarvam(req.text, req.language)
        else:
            audio_bytes = await synthesize_speech(req.text, req.language, req.emotion)

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"}
        )

    except Exception as e:
        # Fallback: try other provider
        try:
            if req.provider == "elevenlabs":
                audio_bytes = await synthesize_sarvam(req.text, req.language)
            else:
                audio_bytes = await synthesize_speech(req.text, req.language, req.emotion)
            return Response(content=audio_bytes, media_type="audio/mpeg")
        except Exception as e2:
            raise HTTPException(500, f"TTS failed on both providers: {e} | {e2}")


@router.get("/languages")
async def supported_languages():
    """Return list of supported languages for TTS."""
    return {
        "languages": [
            {"code": "mr", "name": "Marathi",    "providers": ["elevenlabs", "sarvam"]},
            {"code": "hi", "name": "Hindi",      "providers": ["elevenlabs", "sarvam"]},
            {"code": "ta", "name": "Tamil",      "providers": ["elevenlabs", "sarvam"]},
            {"code": "te", "name": "Telugu",     "providers": ["sarvam"]},
            {"code": "bn", "name": "Bengali",    "providers": ["elevenlabs", "sarvam"]},
            {"code": "gu", "name": "Gujarati",   "providers": ["sarvam"]},
            {"code": "kn", "name": "Kannada",    "providers": ["sarvam"]},
            {"code": "en", "name": "English",    "providers": ["elevenlabs", "sarvam"]},
        ]
    }