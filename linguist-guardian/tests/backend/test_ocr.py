"""
Unit tests for the OCR / document analysis endpoint.
Uses mocked GPT-4o Vision responses.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


MOCK_AADHAAR_RESULT = {
    "doc_type": "aadhaar",
    "extracted_fields": {
        "name": "Priya Sharma",
        "dob": "12/03/1990",
        "address": "Flat 302, Baner Road, Pune 411045",
        "id_number": "XXXX XXXX 4829",
        "issue_date": "",
        "expiry_date": "",
    },
    "cross_check_results": [
        {"field": "name", "status": "match", "detail": ""},
        {"field": "dob", "status": "match", "detail": ""},
        {"field": "address", "status": "mismatch", "detail": "Address from 2018 record"},
    ],
    "mismatches": ["Address does not match current record"],
    "ocr_confidence": 0.97,
    "is_expired": False,
    "staff_action": "Request utility bill (electricity/gas/water) not older than 3 months for address verification.",
    "verification_status": "partial",
    "risk_flags": [],
}

MOCK_PAN_RESULT = {
    "doc_type": "pan",
    "extracted_fields": {
        "name": "Priya Sharma",
        "dob": "12/03/1990",
        "id_number": "BXPPS1234K",
    },
    "cross_check_results": [
        {"field": "name", "status": "match", "detail": ""},
        {"field": "dob", "status": "match", "detail": ""},
    ],
    "mismatches": [],
    "ocr_confidence": 0.99,
    "is_expired": False,
    "staff_action": "PAN verified successfully. Proceed with KYC update.",
    "verification_status": "verified",
    "risk_flags": [],
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
        """Aadhaar with address mismatch should return 'partial' status."""
        with patch("core.gpt4o_client.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_AADHAAR_RESULT)
            )
            from core.gpt4o_client import analyze_document
            result = await analyze_document(
                image_base64="fake_base64_data",
                doc_type="aadhaar",
                customer_record={"name": "Priya Sharma", "dob": "12/03/1990"},
            )

            assert result["doc_type"] == "aadhaar"
            assert result["verification_status"] == "partial"
            assert result["ocr_confidence"] >= 0.95
            assert len(result["mismatches"]) > 0

    @pytest.mark.asyncio
    async def test_pan_full_match(self):
        """PAN with all fields matching should return 'verified' status."""
        with patch("core.gpt4o_client.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_PAN_RESULT)
            )
            from core.gpt4o_client import analyze_document
            result = await analyze_document(
                image_base64="fake_base64_data",
                doc_type="pan",
                customer_record={"name": "Priya Sharma"},
            )

            assert result["verification_status"] == "verified"
            assert len(result["mismatches"]) == 0

    @pytest.mark.asyncio
    async def test_returns_staff_action(self):
        """Result should always include a staff_action instruction."""
        with patch("core.gpt4o_client.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_mock_chat_response(MOCK_AADHAAR_RESULT)
            )
            from core.gpt4o_client import analyze_document
            result = await analyze_document("fake", "aadhaar", {})
            assert "staff_action" in result
            assert len(result["staff_action"]) > 0
