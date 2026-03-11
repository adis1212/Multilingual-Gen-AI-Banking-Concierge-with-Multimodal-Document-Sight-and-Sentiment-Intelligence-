"""
Keyword Spotter — Scan transcripts for banking-related keywords.
Uses pre-defined keyword lists per language to detect urgency and suggest CBS actions.
"""
import json
from pathlib import Path
from typing import Optional

KEYWORDS_DIR = Path(__file__).parent
_keyword_data = {}


def _load_keywords(language: str) -> dict:
    """Load keyword data for a specific language."""
    if language not in _keyword_data:
        file_path = KEYWORDS_DIR / f"keywords_{language}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                _keyword_data[language] = json.load(f)
        else:
            _keyword_data[language] = {"keywords": {}}
    return _keyword_data[language]


def spot_keywords(text: str, language: str = "mr") -> dict:
    """
    Scan text for banking keywords and return matches.

    Args:
        text: Input transcript text
        language: Language code (mr, hi)

    Returns:
        dict with keys: matches, highest_urgency, suggested_actions, total_hits
    """
    if not text or not text.strip():
        return _empty_result()

    data = _load_keywords(language)
    keywords = data.get("keywords", {})

    all_matches = []
    all_actions = set()
    urgency_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    max_urgency_score = 0
    max_urgency_label = "low"

    for category, info in keywords.items():
        terms = info.get("terms", [])
        urgency = info.get("urgency", "low")
        actions = info.get("actions", [])

        matched_terms = [t for t in terms if t in text]

        if matched_terms:
            all_matches.append({
                "category": category,
                "matched_terms": matched_terms,
                "urgency": urgency,
                "actions": actions,
            })
            all_actions.update(actions)

            urgency_score = urgency_levels.get(urgency, 0)
            if urgency_score > max_urgency_score:
                max_urgency_score = urgency_score
                max_urgency_label = urgency

    total_hits = sum(len(m["matched_terms"]) for m in all_matches)

    return {
        "matches": all_matches,
        "highest_urgency": max_urgency_label if all_matches else "none",
        "suggested_actions": sorted(all_actions),
        "total_hits": total_hits,
    }


def _empty_result() -> dict:
    return {
        "matches": [],
        "highest_urgency": "none",
        "suggested_actions": [],
        "total_hits": 0,
    }


def get_supported_languages() -> list[str]:
    """Return list of languages that have keyword files."""
    files = KEYWORDS_DIR.glob("keywords_*.json")
    return [f.stem.replace("keywords_", "") for f in files]
