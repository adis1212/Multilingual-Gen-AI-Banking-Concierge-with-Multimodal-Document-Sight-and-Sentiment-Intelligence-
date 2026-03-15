"""
Unit tests for the OCR / document analysis endpoint.
Uses mocked GPT-4o Vision responses.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


MOCK_AADHAAR_RESULT = {
    "document_type": "Aadhaar Card",
    "name": "Priya Sharma",
    "date_of_birth": "12/03/1990",
    "document_number": "XXXX XXXX 4829",
    "address": "Flat 302, Baner Road, Pune 411045",
    "verification_status": "mismatch",
    "staff_action": "Request utility bill (electricity/gas/water) not older than 3 months for address verification."
}

MOCK_PAN_RESULT = {
    "document_type": "PAN Card",
    "name": "Priya Sharma",
    "date_of_birth": "12/03/1990",
    "document_number": "BXPPS1234K",
    "address": "",
    "verification_status": "valid",
    "staff_action": "PAN verified successfully. Proceed with KYC update."
}


def _mock_chat_response(content_dict):
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = json.dumps(content_dict)
    return mock


class TestDocumentAnalysis:
    """Tests for the analyze_document function."""

    @pytest.mark.asyncio
    async def test_aadhaar_partial_match(self):
        """Aadhaar with address mismatch should return 'mismatch' status."""
        with patch("core.gpt4o_client.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_AADHAAR_RESULT)
            )
            mock_get_client.return_value = mock_client
            from core.gpt4o_client import analyze_document
            result = await analyze_document(
                image_base64="fake_base64_data",
                doc_type="aadhaar",
                customer_record={"name": "Priya Sharma", "dob": "12/03/1990"},
            )

            assert result["document_type"] == "Aadhaar Card"
            assert result["verification_status"] == "mismatch"
            assert len(result["staff_action"]) > 0

    @pytest.mark.asyncio
    async def test_pan_full_match(self):
        """PAN with all fields matching should return 'valid' status."""
        with patch("core.gpt4o_client.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_PAN_RESULT)
            )
            mock_get_client.return_value = mock_client
            from core.gpt4o_client import analyze_document
            result = await analyze_document(
                image_base64="fake_base64_data",
                doc_type="pan",
                customer_record={"name": "Priya Sharma"},
            )

            assert result["verification_status"] == "valid"

    @pytest.mark.asyncio
    async def test_returns_staff_action(self):
        """Result should always include a staff_action instruction."""
        with patch("core.gpt4o_client.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_AADHAAR_RESULT)
            )
            mock_get_client.return_value = mock_client
            from core.gpt4o_client import analyze_document
            result = await analyze_document("fake", "aadhaar", {})
            assert "staff_action" in result
            assert len(result["staff_action"]) > 0
