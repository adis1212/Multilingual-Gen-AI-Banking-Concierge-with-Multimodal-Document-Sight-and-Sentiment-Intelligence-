"""
Unit tests for the Branch Concierge Orchestrator backend.
Tests cover: HTTP validation, noise-only fallback, malformed LLM response,
missing prompt file, empty session context, endpoint registration, and prompt content.
"""
import json
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

# Ensure the backend root is on sys.path so imports resolve correctly
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# ---------------------------------------------------------------------------
# Stub out heavy optional dependencies that are not installed in the test venv
# so that importing main.py doesn't fail on missing native libraries.
# Only stub modules that are genuinely missing — do NOT stub numpy (it's installed)
# ---------------------------------------------------------------------------
_STUB_MODULES = [
    "librosa", "librosa.feature", "librosa.effects",
    "soundfile", "sklearn", "sklearn.preprocessing",
    "joblib", "chromadb", "sentence_transformers",
    "PIL", "PIL.Image",
    "jose", "jose.jwt", "passlib", "passlib.context",
    "multipart",
]
for _mod in _STUB_MODULES:
    if _mod not in sys.modules:
        try:
            __import__(_mod)
        except ImportError:
            sys.modules[_mod] = MagicMock()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_client(response_json: dict | None = None, raw_content: str | None = None):
    """Return a mock OpenAI async client whose chat.completions.create returns the given payload."""
    if raw_content is None:
        raw_content = json.dumps(response_json or {
            "intent": "test_intent",
            "agent": "CUSTOMER_SERVICE_AGENT",
            "urgency": "low",
            "recommended_action": "Test action",
        })
    mock_message = MagicMock()
    mock_message.content = raw_content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


# ---------------------------------------------------------------------------
# Test 1: empty transcript → HTTP 400
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_empty_transcript_returns_400():
    """POST /api/orchestrate with an empty transcript string must return HTTP 400."""
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/orchestrate/",
            json={"transcript": ""},
        )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Test 2: noise-only transcript → fallback without calling GPT-4o
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_noise_only_transcript_fallback():
    """
    route_conversation("[inaudible] [noise]", ...) must return intent=unclear,
    agent=QUEUE_MANAGEMENT_AGENT, urgency=low WITHOUT calling GPT-4o.
    """
    from core.orchestrator import route_conversation

    mock_client = _make_mock_client()

    with patch("core.orchestrator.get_client", return_value=mock_client), \
         patch("core.orchestrator.load_prompt", return_value="system prompt"):
        result = await route_conversation("[inaudible] [noise]", "en", None, [])

    assert result["intent"] == "unclear"
    assert result["agent"] == "QUEUE_MANAGEMENT_AGENT"
    assert result["urgency"] == "low"
    # GPT-4o must NOT have been called
    mock_client.chat.completions.create.assert_not_called()


# ---------------------------------------------------------------------------
# Test 3: malformed LLM response → fallback RoutingDecision
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_malformed_llm_response_fallback():
    """
    When GPT-4o returns 'not json', the endpoint must return the fallback
    RoutingDecision: intent=parse_error, agent=QUEUE_MANAGEMENT_AGENT, urgency=medium.
    """
    from main import app

    mock_client = _make_mock_client(raw_content="not json")

    with patch("core.orchestrator.get_client", return_value=mock_client), \
         patch("core.orchestrator.load_prompt", return_value="system prompt"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/orchestrate/",
                json={"transcript": "I need help with my account"},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "parse_error"
    assert body["agent"] == "QUEUE_MANAGEMENT_AGENT"
    assert body["urgency"] == "medium"


# ---------------------------------------------------------------------------
# Test 4: missing prompt file → FileNotFoundError propagates
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_missing_prompt_file_raises():
    """
    When load_prompt raises FileNotFoundError, route_conversation must propagate it.
    """
    from core.orchestrator import route_conversation

    with patch("core.orchestrator.load_prompt", side_effect=FileNotFoundError("orchestrator_routing.txt not found")), \
         patch("core.orchestrator.get_client", return_value=_make_mock_client()):
        with pytest.raises(FileNotFoundError):
            await route_conversation("I need help", "en", None, [])


# ---------------------------------------------------------------------------
# Test 5: session_id with no transcripts in DB → 200 with valid RoutingDecision
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_session_context_empty_no_error():
    """
    Calling the endpoint with a session_id that has no transcripts in DB
    must return HTTP 200 with a valid RoutingDecision.
    """
    from main import app

    mock_client = _make_mock_client()

    with patch("core.orchestrator.get_client", return_value=mock_client), \
         patch("core.orchestrator.load_prompt", return_value="system prompt"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/orchestrate/",
                json={
                    "transcript": "I need help with my account",
                    "session_id": "nonexistent-session-id-xyz",
                },
            )

    assert response.status_code == 200
    body = response.json()
    assert "intent" in body
    assert "agent" in body
    assert "urgency" in body
    assert "recommended_action" in body


# ---------------------------------------------------------------------------
# Test 6: POST /api/orchestrate is registered
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_endpoint_registered():
    """POST /api/orchestrate must be a registered route in the FastAPI app."""
    from main import app

    mock_client = _make_mock_client()

    with patch("core.orchestrator.get_client", return_value=mock_client), \
         patch("core.orchestrator.load_prompt", return_value="system prompt"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/orchestrate/",
                json={"transcript": "hello"},
            )

    # Any 2xx response confirms the route is registered and reachable
    assert response.status_code in (200, 201)


# ---------------------------------------------------------------------------
# Test 7: orchestrator_routing.txt contains all four agent names
# ---------------------------------------------------------------------------

def test_prompt_file_contains_agent_names():
    """
    The orchestrator_routing.txt prompt file must contain all four agent names.
    """
    prompt_path = BACKEND_DIR / "prompts" / "orchestrator_routing.txt"
    assert prompt_path.exists(), f"Prompt file not found: {prompt_path}"

    content = prompt_path.read_text(encoding="utf-8")
    for agent_name in [
        "CUSTOMER_SERVICE_AGENT",
        "DOCUMENT_VERIFICATION_AGENT",
        "QUEUE_MANAGEMENT_AGENT",
        "COMPLIANCE_MONITOR_AGENT",
    ]:
        assert agent_name in content, f"Agent name '{agent_name}' not found in prompt file"
