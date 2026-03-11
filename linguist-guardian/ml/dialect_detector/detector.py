"""
Dialect Detector — Identifies regional dialect from text using marker-based matching.
Uses the dialect_map.json for dialect-specific markers and phrases.
"""
import json
from pathlib import Path
from typing import Optional

# Load dialect map
DIALECT_MAP_PATH = Path(__file__).parent / "dialect_map.json"
_dialect_data = None


def _load_map() -> dict:
    global _dialect_data
    if _dialect_data is None:
        with open(DIALECT_MAP_PATH, "r", encoding="utf-8") as f:
            _dialect_data = json.load(f)
    return _dialect_data


def detect_dialect(text: str, language: str = "mr") -> dict:
    """
    Detect the regional dialect of given text.

    Args:
        text: Input text (in any Indian language)
        language: Base language code (mr, hi, ta, bn, etc.)

    Returns:
        dict with keys: dialect_code, dialect_name, region, confidence, matched_markers
    """
    if not text or not text.strip():
        return _default_result(language)

    data = _load_map()
    dialects = data.get("dialects", {})

    # Filter to dialects matching the base language
    candidates = {
        k: v for k, v in dialects.items()
        if k.startswith(language + "_")
    }

    if not candidates:
        return _default_result(language)

    best_code = None
    best_score = 0
    best_markers = []

    text_lower = text.lower()

    for code, info in candidates.items():
        markers = info.get("markers", [])
        phrases = info.get("common_phrases", [])
        all_patterns = markers + phrases

        matched = [m for m in all_patterns if m in text or m in text_lower]
        score = len(matched)

        if score > best_score:
            best_score = score
            best_code = code
            best_markers = matched

    if best_code and best_score > 0:
        info = candidates[best_code]
        confidence = min(1.0, best_score / max(len(info.get("markers", [])), 1))
        return {
            "dialect_code": best_code,
            "dialect_name": info["name"],
            "region": info["region"],
            "confidence": round(confidence, 2),
            "matched_markers": best_markers,
        }

    return _default_result(language)


def _default_result(language: str) -> dict:
    """Return a default 'standard' result."""
    names = {"mr": "Standard Marathi", "hi": "Standard Hindi", "ta": "Standard Tamil",
             "bn": "Standard Bengali", "te": "Standard Telugu", "gu": "Standard Gujarati"}
    return {
        "dialect_code": f"{language}_standard",
        "dialect_name": names.get(language, f"Standard {language.upper()}"),
        "region": "Unknown",
        "confidence": 0.0,
        "matched_markers": [],
    }


def get_available_dialects(language: Optional[str] = None) -> list[dict]:
    """Get all available dialects, optionally filtered by language."""
    data = _load_map()
    dialects = data.get("dialects", {})

    results = []
    for code, info in dialects.items():
        if language and not code.startswith(language + "_"):
            continue
        results.append({"code": code, **info})

    return results
