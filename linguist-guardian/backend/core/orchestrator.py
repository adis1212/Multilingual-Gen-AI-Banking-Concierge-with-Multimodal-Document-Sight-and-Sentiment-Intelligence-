import json
import re
from .gpt4o_client import get_client, load_prompt


class OrchestratorParseError(Exception):
    """Raised when the LLM returns a malformed or non-JSON routing response."""
    pass


# Distress keywords that unconditionally force urgency=high (Requirement 2.4)
_DISTRESS_KEYWORDS = frozenset(["fraud", "stolen", "emergency", "urgent"])

# Noise-only token pattern — transcripts consisting solely of these produce urgency=low
_NOISE_ONLY_PATTERN = re.compile(
    r"^\s*(\[(inaudible|noise|background noise|silence)\]\s*)+$",
    re.IGNORECASE,
)


def _contains_distress_keyword(transcript: str) -> bool:
    """Return True if the transcript contains any distress keyword (case-insensitive)."""
    lower = transcript.lower()
    return any(kw in lower for kw in _DISTRESS_KEYWORDS)


def _is_noise_only(transcript: str) -> bool:
    """Return True if the transcript contains only non-linguistic noise tokens."""
    return bool(_NOISE_ONLY_PATTERN.match(transcript))


def _is_short_transcript(transcript: str) -> bool:
    """Return True if the transcript has fewer than 5 words."""
    return len(transcript.split()) < 5


async def route_conversation(
    transcript: str,
    language: str,
    sentiment: dict | None,
    prior_context: list[dict],
) -> dict:
    """
    Classify customer intent and return a RoutingDecision dict.

    Args:
        transcript:    The customer's speech-to-text output.
        language:      ISO 639-1 language code (e.g. "en", "hi", "mr").
        sentiment:     Optional dict with keys "emotion" and "stress_level".
        prior_context: Up to 3 recent transcript rows from the same session.

    Returns:
        A dict with keys: intent, agent, urgency, recommended_action.

    Raises:
        OrchestratorParseError: If the LLM response cannot be parsed as JSON.
    """
    # Pre-processing: noise-only transcripts bypass the LLM entirely (Requirement 3.3)
    if _is_noise_only(transcript):
        return {
            "intent": "unclear",
            "agent": "QUEUE_MANAGEMENT_AGENT",
            "urgency": "low",
            "recommended_action": "Ask customer to repeat their request clearly",
        }

    client = get_client()
    system_prompt = load_prompt("orchestrator_routing")

    # Build the user message
    parts = [
        f"Language: {language}",
        f"Transcript: {transcript}",
    ]

    if sentiment is not None:
        parts.append(f"Sentiment Signal: {json.dumps(sentiment)}")
    else:
        parts.append("Sentiment Signal: null")

    if prior_context:
        parts.append(f"Prior Context: {json.dumps(prior_context)}")
    else:
        parts.append("Prior Context: []")

    user_message = "\n".join(parts)

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        max_tokens=400,
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    try:
        decision = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise OrchestratorParseError(
            f"LLM returned a non-JSON response: {raw!r}"
        ) from exc

    # Post-processing overrides — applied after LLM response to guarantee correctness

    # 4.2: Distress keywords unconditionally force urgency=high (Requirement 2.4)
    # This overrides whatever urgency the LLM assigned, including when sentiment is low/absent.
    if _contains_distress_keyword(transcript):
        decision["urgency"] = "high"

    # 4.1: Sentiment-based urgency enforcement when no distress keyword is present
    elif sentiment is not None:
        emotion = sentiment.get("emotion", "")
        stress = sentiment.get("stress_level")
        if emotion == "distressed" or (isinstance(stress, (int, float)) and stress > 0.6):
            decision["urgency"] = "high"
        elif emotion == "frustrated" or (
            isinstance(stress, (int, float)) and 0.3 <= stress <= 0.6
        ):
            if decision.get("urgency") != "high":
                decision["urgency"] = "medium"

    # 4.3: Short transcripts default to urgency=medium and fall back to QUEUE_MANAGEMENT_AGENT
    # when routing is ambiguous (intent=unclear). Only applies if urgency not already high.
    if _is_short_transcript(transcript) and decision.get("urgency") != "high":
        # Any urgency that isn't already high becomes medium (requirement 3.1)
        if decision.get("urgency") != "medium":
            decision["urgency"] = "medium"
        if decision.get("intent") == "unclear":
            decision["agent"] = "QUEUE_MANAGEMENT_AGENT"

    return decision
