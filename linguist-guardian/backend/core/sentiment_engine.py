import numpy as np
import librosa
import io
from dataclasses import dataclass


@dataclass
class SentimentResult:
    stress_level: float      # 0.0 to 1.0
    pitch_rise_pct: float    # % above baseline
    speech_rate: str         # "slow" | "normal" | "fast"
    volume: str              # "low" | "medium" | "high"
    emotion: str             # "calm" | "neutral" | "frustrated" | "distressed"
    deescalate: bool         # True if action needed
    tips: list[str]


# Baseline pitch for normal speech (Hz)
BASELINE_PITCH = 180.0
PITCH_ANGER_THRESHOLD = 0.20   # 20% rise triggers alert


async def analyze_audio_sentiment(audio_bytes: bytes) -> SentimentResult:
    """
    Analyze pitch, speech rate, volume from raw audio bytes.
    Uses librosa for signal processing.
    """
    try:
        # Load audio
        audio_array, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=22050,
            mono=True
        )

        # 1. Pitch analysis (F0 estimation)
        f0, voiced_flag, _ = librosa.pyin(
            audio_array,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7')
        )
        voiced_f0 = f0[voiced_flag]
        mean_pitch = float(np.nanmean(voiced_f0)) if len(voiced_f0) > 0 else BASELINE_PITCH
        pitch_rise = (mean_pitch - BASELINE_PITCH) / BASELINE_PITCH

        # 2. Speech rate (syllables per second approximation)
        onset_frames = librosa.onset.onset_detect(y=audio_array, sr=sr)
        duration = librosa.get_duration(y=audio_array, sr=sr)
        rate = len(onset_frames) / max(duration, 1)
        speech_rate = "fast" if rate > 6 else ("slow" if rate < 3 else "normal")

        # 3. Volume (RMS energy)
        rms = float(np.mean(librosa.feature.rms(y=audio_array)))
        volume = "high" if rms > 0.05 else ("low" if rms < 0.01 else "medium")

        # 4. Composite stress score
        stress = min(1.0, max(0.0,
            (pitch_rise * 0.5) +
            (0.3 if speech_rate == "fast" else 0.0) +
            (0.2 if volume == "high" else 0.0)
        ))

        # 5. Emotion label
        if stress > 0.7:
            emotion = "distressed"
        elif stress > 0.5:
            emotion = "frustrated"
        elif stress > 0.3:
            emotion = "neutral"
        else:
            emotion = "calm"

        deescalate = pitch_rise > PITCH_ANGER_THRESHOLD or stress > 0.6

        tips = []
        if deescalate:
            tips = [
                "Offer complimentary refreshment",
                "Prioritize this token immediately",
                "Use a slower, empathetic tone",
                "Address them respectfully (e.g., 'ji')",
            ]

        return SentimentResult(
            stress_level=round(stress, 2),
            pitch_rise_pct=round(pitch_rise * 100, 1),
            speech_rate=speech_rate,
            volume=volume,
            emotion=emotion,
            deescalate=deescalate,
            tips=tips,
        )

    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return SentimentResult(0.0, 0.0, "normal", "medium", "neutral", False, [])