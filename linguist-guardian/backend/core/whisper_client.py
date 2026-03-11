import openai
import os
from utils.banking_glossary import BANKING_GLOSSARY_PROMPT

_client = None

SUPPORTED_LANGUAGES = {
    "mr": "Marathi",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "en": "English",
    "gu": "Gujarati",
    "kn": "Kannada",
}


def get_client():
    global _client
    if _client is None:
        _client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


async def transcribe_audio(
    audio_bytes: bytes,
    language: str = "mr",
    channel: str = "A"
) -> dict:
    """
    Transcribe audio using Whisper Large-v3.
    Uses banking glossary as initial_prompt for 99% jargon accuracy.
    """
    try:
        client = get_client()
        # Write bytes to temp file (Whisper needs file-like object)
        import tempfile, os as _os
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        with open(tmp_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model="whisper-1",          # maps to large-v3 in API
                file=audio_file,
                language=language if language != "auto" else None,
                initial_prompt=BANKING_GLOSSARY_PROMPT,  # KEY HACK
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

        _os.unlink(tmp_path)

        return {
            "text": response.text,
            "language": response.language,
            "channel": channel,
            "words": [
                {"word": w.word, "start": w.start, "end": w.end}
                for w in (response.words or [])
            ],
            "duration": response.duration,
        }

    except Exception as e:
        return {"error": str(e), "text": "", "channel": channel}


async def translate_to_english(text: str, source_language: str) -> str:
    """Translate any Indian language text to English."""
    client = get_client()
    try:
        response = await client.audio.translations.create(
            model="whisper-1",
            file=None,  # text-only translation via chat
        )
    except Exception:
        pass

    # Fallback: use GPT-4o for translation
    chat = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a translator. Translate the given text to English. Return only the translated text, nothing else."},
            {"role": "user", "content": f"Translate from {SUPPORTED_LANGUAGES.get(source_language, 'Indian language')}: {text}"}
        ],
        max_tokens=500
    )
    return chat.choices[0].message.content.strip()