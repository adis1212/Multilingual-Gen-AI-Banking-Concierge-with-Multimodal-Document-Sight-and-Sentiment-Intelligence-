"""
AGENT 2 — Document Verification Agent
Purpose: Verify customer identity documents during KYC processes.
Supports: Aadhaar, PAN, Passport, Driving Licence, Voter ID, Bank Passbook.
Returns the exact structured JSON specified in the Master Prompt.
"""

import json
import logging
from core.gpt4o_client import get_client, load_prompt

logger = logging.getLogger(__name__)

# The document_analysis.txt prompt already returns the correct JSON schema.
# This agent wraps it for both image-based (GPT-4o Vision) and text-based verification.


async def verify_from_image(image_base64: str, doc_type: str = "aadhaar", customer_record: dict | None = None) -> dict:
    """
    Verify a document from a camera/upload image using GPT-4o Vision.
    Returns Master-Prompt-compliant JSON.
    """
    client = get_client()
    system_prompt = load_prompt("document_analysis")
    record = customer_record or {}

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Document type hint: {doc_type}\n"
                            f"Customer record on file: {json.dumps(record)}\n"
                            "Analyze this document image and verify it."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ]},
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
        )

        result = json.loads(response.choices[0].message.content)
        return _normalise(result)

    except Exception as exc:
        logger.error("DocumentVerificationAgent image error: %s", exc)
        return _fallback(doc_type)


async def verify_from_text(ocr_text: str, doc_type: str = "aadhaar", customer_record: dict | None = None) -> dict:
    """
    Verify a document from pre-extracted OCR text (non-vision path).
    """
    client = get_client()
    system_prompt = load_prompt("document_analysis")
    record = customer_record or {}

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": (
                    f"Document type hint: {doc_type}\n"
                    f"Customer record on file: {json.dumps(record)}\n"
                    f"OCR-extracted text:\n{ocr_text}\n\n"
                    "Analyze and verify this document."
                )},
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
            temperature=0.1,
        )

        result = json.loads(response.choices[0].message.content)
        return _normalise(result)

    except Exception as exc:
        logger.error("DocumentVerificationAgent text error: %s", exc)
        return _fallback(doc_type)


def _normalise(result: dict) -> dict:
    """Ensure the output conforms exactly to the Master Prompt schema."""
    return {
        "document_type": result.get("document_type", ""),
        "name": result.get("name", ""),
        "date_of_birth": result.get("date_of_birth", ""),
        "document_number": result.get("document_number", ""),
        "address": result.get("address", ""),
        "verification_status": result.get("verification_status", "manual_review_required"),
        "staff_action": result.get("staff_action", "Review document manually."),
    }


def _fallback(doc_type: str) -> dict:
    return {
        "document_type": doc_type,
        "name": "",
        "date_of_birth": "",
        "document_number": "",
        "address": "",
        "verification_status": "manual_review_required",
        "staff_action": "System could not auto-verify. Please review document manually.",
    }
