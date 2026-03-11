from fastapi import APIRouter, UploadFile, File
from core.sentiment_engine import analyze_audio_sentiment

router = APIRouter()


@router.post("/analyze")
async def analyze_sentiment(audio: UploadFile = File(...)):
    """Analyze emotional state from customer audio."""
    audio_bytes = await audio.read()
    result = await analyze_audio_sentiment(audio_bytes)

    return {
        "stress_level": result.stress_level,
        "pitch_rise_pct": result.pitch_rise_pct,
        "speech_rate": result.speech_rate,
        "volume": result.volume,
        "emotion": result.emotion,
        "deescalate": result.deescalate,
        "tips": result.tips,
    }