"""Unit tests for Master AI Concierge orchestration."""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))


def _make_mock_client(intent: str):
    payload = {"intent": intent}
    mock_message = MagicMock()
    mock_message.content = json.dumps(payload)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.mark.asyncio
async def test_classify_intent_keyword_fallback_when_llm_returns_unknown():
    from agents.master_concierge import classify_intent

    mock_client = _make_mock_client("something_else")
    with patch("agents.master_concierge.get_client", return_value=mock_client):
        intent = await classify_intent("I need a token for queue")

    assert intent == "token_request"


@pytest.mark.asyncio
async def test_process_request_routes_customer_service_agent():
    from agents.master_concierge import process_request

    with patch("agents.master_concierge.classify_intent", AsyncMock(return_value="account_service")), patch(
        "agents.master_concierge.customer_service_agent.handle",
        AsyncMock(return_value={"response": "Namaste. How may I help you?", "staff_action": "Assist at support desk."}),
    ):
        result = await process_request("Need account balance", customer_name="Asha")

    assert result["intent"] == "account_service"
    assert result["agent_used"] == "CUSTOMER_SERVICE_AGENT"
    assert result["response"]
    assert result["staff_action"]
    assert result["document_verification"] is None


@pytest.mark.asyncio
async def test_process_request_document_text_runs_verification():
    from agents.master_concierge import process_request

    verification = {
        "document_type": "pan",
        "name": "Ravi Kumar",
        "date_of_birth": "1990-01-01",
        "document_number": "ABCDE1234F",
        "address": "",
        "verification_status": "valid",
        "staff_action": "Proceed with KYC.",
    }

    with patch("agents.master_concierge.classify_intent", AsyncMock(return_value="document_verification")), patch(
        "agents.master_concierge.document_verification_agent.verify_from_text",
        AsyncMock(return_value=verification),
    ):
        result = await process_request(
            "PAN Name Ravi Kumar DOB 1990-01-01 Number ABCDE1234F",
            customer_name="Ravi",
        )

    assert result["agent_used"] == "DOCUMENT_VERIFICATION_AGENT"
    assert result["document_verification"] == verification
    assert "valid" in result["response"].lower()
    assert result["staff_action"] == "Proceed with KYC."


@pytest.mark.asyncio
async def test_process_request_attaches_compliance_result():
    from agents.master_concierge import process_request

    compliance = {
        "compliance_status": "warning",
        "issue_detected": "Missing KYC confirmation",
        "recommended_action": "Verify KYC before proceeding",
    }

    with patch("agents.master_concierge.classify_intent", AsyncMock(return_value="general_help")), patch(
        "agents.master_concierge.customer_service_agent.handle",
        AsyncMock(return_value={"response": "Namaste. How may I assist?", "staff_action": "Collect customer details."}),
    ), patch("agents.master_concierge.compliance_monitor_agent.monitor", AsyncMock(return_value=compliance)):
        result = await process_request(
            "Hello",
            staff_utterance="We will process without checking KYC",
        )

    assert result["agent_used"] == "CUSTOMER_SERVICE_AGENT"
    assert result["compliance"] == compliance
