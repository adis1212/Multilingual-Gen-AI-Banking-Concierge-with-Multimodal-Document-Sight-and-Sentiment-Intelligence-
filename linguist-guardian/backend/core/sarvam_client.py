import httpx
import os

BASE_URL       = "https://api.sarvam.ai"

# Sarvam language codes
LANGUAGE_MAP = {
    "mr": "mr-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "bn": "bn-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "en": "en-IN",
}

# Speaker voices — professional Indian bank staff tone
SPEAKER_MAP = {
    "mr": "anushka",
    "hi": "anushka",
    "ta": "anushka",
    "te": "anushka",
    "bn": "anushka",
    "en": "anushka",
}


async def synthesize_sarvam(text: str, language: str = "hi") -> bytes:
    """
    Convert text to speech using Sarvam AI.
    Best for Indian regional languages — better accent & naturalness than ElevenLabs.
    """
    lang_code = LANGUAGE_MAP.get(language, "hi-IN")
    speaker   = SPEAKER_MAP.get(language, "anushka")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/text-to-speech",
            headers={
                "api-subscription-key": os.getenv("SARVAM_API_KEY"),
                "Content-Type": "application/json",
            },
            json={
                "inputs":         [text],
                "target_language_code": lang_code,
                "speaker":        speaker,
                "pitch":          0,
                "pace":           0.9,       # slightly slower = more empathetic
                "loudness":       1.5,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
                "model":          "bulbul:v1",
            }
        )
        response.raise_for_status()
        data = response.json()

        # Sarvam returns base64 audio
        import base64
        audio_b64 = data["audios"][0]
        return base64.b64decode(audio_b64)


async def transcribe_sarvam(audio_bytes: bytes, language: str = "mr") -> dict:
    """
    Sarvam STT — fallback for Whisper when Indian dialect accuracy is needed.
    Especially good for code-switched speech (Marathinglish, Hinglish).
    """
    import tempfile, os, base64

    lang_code = LANGUAGE_MAP.get(language, "hi-IN")

    # Encode audio to base64
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{BASE_URL}/speech-to-text",
            headers={
                "api-subscription-key": os.getenv("SARVAM_API_KEY"),
                "Content-Type": "application/json",
            },
            json={
                "model":                  "saarika:v2",
                "language_code":          lang_code,
                "with_timestamps":        False,
                "with_disfluencies":      False,
                "audio":                  audio_b64,
            }
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text":     data.get("transcript", ""),
            "language": language,
            "provider": "sarvam",
        }


async def translate_sarvam(text: str, source: str, target: str = "en") -> str:
    """
    Sarvam translation — Indian language ↔ English.
    More accurate than Whisper for colloquial Indian speech.
    """
    source_code = LANGUAGE_MAP.get(source, "hi-IN")
    target_code = LANGUAGE_MAP.get(target, "en-IN")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/translate",
            headers={
                "api-subscription-key": os.getenv("SARVAM_API_KEY"),
                "Content-Type": "application/json",
            },
            json={
                "input":                text,
                "source_language_code": source_code,
                "target_language_code": target_code,
                "speaker_gender":       "Female",
                "mode":                 "formal",
                "model":                "mayura:v1",
                "enable_preprocessing": True,
            }
        )
        response.raise_for_status()
        return response.json().get("translated_text", text)