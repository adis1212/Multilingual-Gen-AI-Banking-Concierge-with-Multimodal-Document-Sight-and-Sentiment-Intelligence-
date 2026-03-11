import httpx
import os

BASE_URL = "https://api.elevenlabs.io/v1"

# Voice IDs — pick empathetic, professional Indian-accented voices
VOICE_MAP = {
    "mr": "your-marathi-voice-id",
    "hi": "your-hindi-voice-id",
    "ta": "your-tamil-voice-id",
    "te": "your-telugu-voice-id",
    "bn": "your-bengali-voice-id",
    "en": "your-english-voice-id",
}

DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"   # Rachel — warm & professional


async def synthesize_speech(
    text: str,
    language: str = "hi",
    emotion: str = "neutral"
) -> bytes:
    """
    Convert staff response to customer's language audio.
    Adjusts stability/similarity for empathetic tone when customer is stressed.
    """
    voice_id = VOICE_MAP.get(language, DEFAULT_VOICE)

    # Tune voice settings based on customer emotion
    stability     = 0.4 if emotion in ["distressed", "frustrated"] else 0.6
    similarity    = 0.8
    style         = 0.3 if emotion in ["distressed", "frustrated"] else 0.1

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity,
                    "style": style,
                    "use_speaker_boost": True,
                }
            }
        )
        response.raise_for_status()
        return response.content   # raw MP3 bytes