"""
Audio utility functions for format conversion, resampling, and analysis.
Used across the backend for preprocessing audio before sending to AI models.
"""
import io
import tempfile
import os
import base64
import numpy as np

try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    import librosa
except ImportError:
    librosa = None


def webm_to_wav(webm_bytes: bytes, target_sr: int = 16000) -> bytes:
    """
    Convert WebM/Opus audio bytes to WAV format.
    Whisper and Sarvam prefer WAV with 16kHz sample rate.
    """
    if librosa is None:
        raise ImportError("librosa is required for audio conversion")

    audio, sr = librosa.load(io.BytesIO(webm_bytes), sr=target_sr, mono=True)

    wav_buffer = io.BytesIO()
    if sf:
        sf.write(wav_buffer, audio, target_sr, format="WAV")
    else:
        # Fallback: raw PCM in a BytesIO
        wav_buffer.write(audio.tobytes())
    wav_buffer.seek(0)
    return wav_buffer.read()


def bytes_to_temp_file(audio_bytes: bytes, suffix: str = ".webm") -> str:
    """
    Write audio bytes to a named temporary file.
    Returns the file path. Caller must delete the file when done.
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        return f.name


def cleanup_temp_file(path: str) -> None:
    """Safely delete a temporary file."""
    try:
        if path and os.path.exists(path):
            os.unlink(path)
    except OSError:
        pass


def get_audio_duration(audio_bytes: bytes) -> float:
    """
    Get duration of audio in seconds.
    Returns 0.0 if unable to determine.
    """
    if librosa is None:
        return 0.0
    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
        return float(librosa.get_duration(y=audio, sr=sr))
    except Exception:
        return 0.0


def audio_to_base64(audio_bytes: bytes) -> str:
    """Encode raw audio bytes to base64 string."""
    return base64.b64encode(audio_bytes).decode("utf-8")


def base64_to_audio(b64_string: str) -> bytes:
    """Decode a base64 string back to raw audio bytes."""
    return base64.b64decode(b64_string)


def resample_audio(audio_bytes: bytes, target_sr: int = 22050) -> bytes:
    """
    Resample audio to a target sample rate.
    Returns resampled audio as raw float32 bytes.
    """
    if librosa is None:
        return audio_bytes
    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=target_sr, mono=True)
        return audio.tobytes()
    except Exception:
        return audio_bytes


def compute_rms(audio_bytes: bytes) -> float:
    """
    Compute root-mean-square energy of audio.
    Returns 0.0 on failure.
    """
    if librosa is None:
        return 0.0
    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=22050, mono=True)
        return float(np.mean(librosa.feature.rms(y=audio)))
    except Exception:
        return 0.0
