"""
Unit tests for the intent extraction and compliance check endpoints.
Uses mocked GPT-4o responses to avoid real API calls.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


# ── Mock GPT-4o response fixtures ─────────────────────────
MOCK_INTENT_RESPONSE = {
    "intent": "lost_card",
    "urgency": "critical",
    "emotion": "distressed",
    "stress_keywords": ["lost", "worried"],
    "staff_advisory": "Initiate card block immediately. Customer is distressed.",
    "suggested_actions": ["block_card", "reissue_card"],
    "banking_processes": ["CARD_BLOCK", "CARD_REISSUE"],
    "response_in_customer_language": "काळजी करू नका, आम्ही आत्ताच तुमचे कार्ड ब्लॉक करतो.",
    "escalate_to_manager": False,
}

MOCK_COMPLIANCE_RESPONSE = {
    "compliant": True,
    "violations": [],
    "warning_message": "",
    "severity": "none",
}

MOCK_NONCOMPLIANT_RESPONSE = {
    "compliant": False,
    "violations": ["Did not disclose that insurance is not a bank product"],
    "warning_message": "Staff must inform customer that insurance is offered by third-party.",
    "severity": "high",
}


# ── Helper to create mock OpenAI response ──────────────────
def _mock_chat_response(content_dict):
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = json.dumps(content_dict)
    return mock


# ── Tests ────────────────────────────────────────────────

class TestExtractIntent:
    """Tests for the extract_intent function."""

    @pytest.mark.asyncio
    async def test_lost_card_intent(self):
        """Should extract lost_card intent from Marathi transcript."""
        with patch("core.gpt4o_client.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_INTENT_RESPONSE)
            )

            from core.gpt4o_client import extract_intent
            result = await extract_intent(
                "मला माझे कार्ड हरवले आहे",
                language="mr",
                customer_context={},
            )

            assert result["intent"] == "lost_card"
            assert result["urgency"] == "critical"
            assert result["emotion"] == "distressed"
            assert "CARD_BLOCK" in result["banking_processes"]

    @pytest.mark.asyncio
    async def test_empty_transcript_returns_error(self):
        """Empty transcript should be handled gracefully."""
        # The route-level validation raises HTTPException for empty text
        # Here we test that the function itself handles an empty string
        with patch("core.gpt4o_client.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response({"intent": "other", "urgency": "low", "emotion": "neutral"})
            )
            from core.gpt4o_client import extract_intent
            result = await extract_intent("", language="en")
            assert "intent" in result


class TestComplianceCheck:
    """Tests for the compliance check function."""

    @pytest.mark.asyncio
    async def test_compliant_utterance(self):
        """A proper staff utterance should pass compliance."""
        with patch("core.gpt4o_client.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_COMPLIANCE_RESPONSE)
            )
            from core.gpt4o_client import check_compliance
            result = await check_compliance("Your new card will be ready in 3 business days.")
            assert result["compliant"] is True
            assert len(result["violations"]) == 0

    @pytest.mark.asyncio
    async def test_noncompliant_insurance_pitch(self):
        """Staff selling insurance without disclosure should be flagged."""
        with patch("core.gpt4o_client.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_NONCOMPLIANT_RESPONSE)
            )
            from core.gpt4o_client import check_compliance
            result = await check_compliance("You should buy our premium insurance plan.")
            assert result["compliant"] is False
            assert result["severity"] == "high"
            assert len(result["violations"]) > 0
