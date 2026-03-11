"""
Unit tests for the Whisper transcription module.
Uses mocked OpenAI Whisper API responses.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


MOCK_WHISPER_RESPONSE = MagicMock()
MOCK_WHISPER_RESPONSE.text = "मला माझे कार्ड हरवले आहे"
MOCK_WHISPER_RESPONSE.language = "mr"
MOCK_WHISPER_RESPONSE.duration = 3.5
MOCK_WHISPER_RESPONSE.words = [
    MagicMock(word="मला", start=0.0, end=0.5),
    MagicMock(word="माझे", start=0.5, end=1.0),
    MagicMock(word="कार्ड", start=1.0, end=1.5),
    MagicMock(word="हरवले", start=1.5, end=2.0),
    MagicMock(word="आहे", start=2.0, end=2.5),
]


MOCK_TRANSLATION_RESPONSE = MagicMock()
MOCK_TRANSLATION_RESPONSE.choices = [MagicMock()]
MOCK_TRANSLATION_RESPONSE.choices[0].message.content = "I lost my card"


class TestTranscribeAudio:
    """Tests for the transcribe_audio function."""

    @pytest.mark.asyncio
    async def test_marathi_transcription(self):
        """Should transcribe Marathi audio and return text with word timestamps."""
        with patch("core.whisper_client.client") as mock_client:
            mock_client.audio.transcriptions.create = AsyncMock(
                return_value=MOCK_WHISPER_RESPONSE
            )

            from core.whisper_client import transcribe_audio
            result = await transcribe_audio(
                audio_bytes=b"fake_audio_data",
                language="mr",
                channel="A",
            )

            assert result["text"] == "मला माझे कार्ड हरवले आहे"
            assert result["language"] == "mr"
            assert result["channel"] == "A"
            assert len(result["words"]) == 5
            assert result["duration"] == 3.5

    @pytest.mark.asyncio
    async def test_english_transcription(self):
        """English transcription should skip translation."""
        mock_en = MagicMock()
        mock_en.text = "I want to check my balance"
        mock_en.language = "en"
        mock_en.duration = 2.0
        mock_en.words = []

        with patch("core.whisper_client.client") as mock_client:
            mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_en)

            from core.whisper_client import transcribe_audio
            result = await transcribe_audio(b"fake_audio", language="en", channel="B")

            assert result["language"] == "en"
            assert result["text"] == "I want to check my balance"

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Should return error dict if Whisper API fails."""
        with patch("core.whisper_client.client") as mock_client:
            mock_client.audio.transcriptions.create = AsyncMock(
                side_effect=Exception("API rate limit exceeded")
            )

            from core.whisper_client import transcribe_audio
            result = await transcribe_audio(b"fake_audio", language="mr")

            assert "error" in result
            assert result["text"] == ""


class TestTranslateToEnglish:
    """Tests for the translate_to_english function."""

    @pytest.mark.asyncio
    async def test_marathi_to_english(self):
        """Should translate Marathi text to English via GPT-4o."""
        with patch("core.whisper_client.client") as mock_client:
            # First call (Whisper translation) raises error → falls through to GPT-4o
            mock_client.audio.translations.create = AsyncMock(
                side_effect=Exception("Not supported")
            )
            mock_client.chat.completions.create = AsyncMock(
                return_value=MOCK_TRANSLATION_RESPONSE
            )

            from core.whisper_client import translate_to_english
            result = await translate_to_english("मला माझे कार्ड हरवले आहे", "mr")

            assert result == "I lost my card"
