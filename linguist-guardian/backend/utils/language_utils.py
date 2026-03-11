"""
Language detection and script identification utilities.
Detects Indian languages from text using Unicode block analysis.
"""
import re
from typing import Optional

# ── Supported languages ──────────────────────────────────
SUPPORTED_LANGUAGES = {
    "mr": "Marathi",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "en": "English",
}

# ── Unicode script ranges ────────────────────────────────
SCRIPT_PATTERNS = {
    "devanagari":  re.compile(r"[\u0900-\u097F]"),    # Hindi, Marathi, Sanskrit
    "bengali":     re.compile(r"[\u0980-\u09FF]"),
    "gurmukhi":    re.compile(r"[\u0A00-\u0A7F]"),    # Punjabi
    "gujarati":    re.compile(r"[\u0A80-\u0AFF]"),
    "tamil":       re.compile(r"[\u0B80-\u0BFF]"),
    "telugu":      re.compile(r"[\u0C00-\u0C7F]"),
    "kannada":     re.compile(r"[\u0C80-\u0CFF]"),
    "malayalam":   re.compile(r"[\u0D00-\u0D7F]"),
}

SCRIPT_TO_LANG = {
    "devanagari": "hi",   # Default; Marathi uses same script
    "bengali":    "bn",
    "gurmukhi":   "pa",
    "gujarati":   "gu",
    "tamil":      "ta",
    "telugu":     "te",
    "kannada":    "kn",
    "malayalam":  "ml",
}

# ── Marathi-specific markers ─────────────────────────────
# Common Marathi words / affixes that distinguish it from Hindi
MARATHI_MARKERS = [
    "आहे", "नाही", "आम्ही", "तुम्ही", "मला",
    "होते", "करतो", "करते", "केले", "झाले",
    "कृपया", "धन्यवाद", "हवे", "पाहिजे",
]


def detect_script(text: str) -> Optional[str]:
    """
    Detect the dominant Unicode script in text.
    Returns script name (e.g. 'devanagari', 'tamil') or None.
    """
    if not text or not text.strip():
        return None

    scores = {}
    clean = text.replace(" ", "")
    total = len(clean)
    if total == 0:
        return None

    for name, pattern in SCRIPT_PATTERNS.items():
        count = len(pattern.findall(text))
        scores[name] = count / total

    best = max(scores, key=scores.get)
    return best if scores[best] > 0.1 else None


def detect_language(text: str) -> str:
    """
    Detect language code from text.
    Returns ISO 639-1 code (e.g. 'hi', 'mr', 'ta', 'en').
    """
    script = detect_script(text)

    if script is None:
        return "en"

    lang = SCRIPT_TO_LANG.get(script, "en")

    # Devanagari disambiguation: Hindi vs Marathi
    if script == "devanagari":
        marathi_count = sum(1 for marker in MARATHI_MARKERS if marker in text)
        if marathi_count >= 2:
            return "mr"
        return "hi"

    return lang


def get_language_name(code: str) -> str:
    """Get display name for a language code."""
    return SUPPORTED_LANGUAGES.get(code, code.upper())


def is_supported(code: str) -> bool:
    """Check if a language code is supported."""
    return code in SUPPORTED_LANGUAGES


def get_all_languages() -> list[dict]:
    """Return all supported languages as a list of dicts."""
    return [{"code": k, "name": v} for k, v in SUPPORTED_LANGUAGES.items()]
