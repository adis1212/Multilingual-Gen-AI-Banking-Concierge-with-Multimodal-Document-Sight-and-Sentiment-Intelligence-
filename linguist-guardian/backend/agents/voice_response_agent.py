"""
AGENT 5 — Voice Response Agent
Purpose: Generate voice responses for customers using text-to-speech.

Voice Requirements: Calm, Clear, Slow, Friendly, Professional.
Rules: Maximum 2 sentences, simple banking language, avoid technical terms,
       be respectful to elderly customers.
"""

import logging
from core.elevenlabs_client import synthesize_speech
from core.sarvam_client import synthesize_sarvam

logger = logging.getLogger(__name__)

# Languages best served by Sarvam (native Indian TTS)
SARVAM_PREFERRED = {"mr", "hi", "ta", "te", "bn", "gu", "kn", "ml"}


async def speak(
    text: str,
    language: str = "en",
    emotion: str = "calm",
    provider: str | None = None,
) -> bytes:
    """
    Convert a short text response into natural speech audio bytes (MP3).

    Provider selection:
    - If provider is explicitly set, use it.
    - Otherwise auto-select: Sarvam for Indian languages, ElevenLabs for English.

    The text should already be ≤2 sentences and in simple banking language
    (enforced by the upstream agent that generated it).
    """
    chosen = provider or ("sarvam" if language in SARVAM_PREFERRED else "elevenlabs")

    try:
        if chosen == "sarvam":
            return await synthesize_sarvam(text, language)
        else:
            return await synthesize_speech(text, language, emotion)

    except Exception as primary_err:
        logger.warning("VoiceResponseAgent primary (%s) failed: %s — trying fallback", chosen, primary_err)
        # Fallback to the other provider
        try:
            if chosen == "sarvam":
                return await synthesize_speech(text, language, emotion)
            else:
                return await synthesize_sarvam(text, language)
        except Exception as fallback_err:
            logger.error("VoiceResponseAgent fallback also failed: %s", fallback_err)
            raise RuntimeError(
                f"Voice synthesis failed on both providers: {primary_err} | {fallback_err}"
            )


def format_for_voice(text: str, customer_name: str = "", language: str = "en") -> str:
    """
    Ensure a text string meets Voice Response Agent rules:
    - Max 2 sentences
    - Simple language
    - Starts with a respectful greeting
    """
    # Truncate to 2 sentences if needed
    sentences = text.replace("。", ".").split(".")
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) > 2:
        sentences = sentences[:2]

    output = ". ".join(sentences)
    if not output.endswith("."):
        output += "."

    # Prepend greeting if not already present
    greetings = ["namaste", "welcome", "hello", "namaskar"]
    if not any(output.lower().startswith(g) for g in greetings):
        name_part = f", {customer_name}" if customer_name else ""
        output = f"Namaste{name_part}. {output}"

    return output
