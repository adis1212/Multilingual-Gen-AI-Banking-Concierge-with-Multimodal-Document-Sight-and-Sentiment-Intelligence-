"""
/api/concierge/ — Master AI Concierge REST endpoints.
This is the single entry-point that coordinates all 5 agents.
"""

import base64
import json
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel

from agents.master_concierge import process_request
from agents import document_verification_agent
from agents import compliance_monitor_agent
from agents import voice_response_agent
from agents import queue_management_agent

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request / Response schemas ──

class ConciergeRequest(BaseModel):
    message: str
    language: str = "en"
    customer_name: str = ""
    session_id: str = ""
    staff_utterance: str | None = None  # optional: triggers compliance check


class ConciergeResponse(BaseModel):
    intent: str
    agent_used: str
    response: str
    staff_action: str
    compliance: dict | None = None
    document_verification: dict | None = None


class ComplianceCheckRequest(BaseModel):
    staff_utterance: str
    session_context: str = ""


class ComplianceCheckResponse(BaseModel):
    compliance_status: str
    issue_detected: str
    recommended_action: str


class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    emotion: str = "calm"
    provider: str | None = None


class VerifyDocumentTextRequest(BaseModel):
    ocr_text: str
    doc_type: str = "aadhaar"
    customer_record: dict = {}


# ── Endpoints ──

@router.post("/", response_model=ConciergeResponse)
async def concierge(req: ConciergeRequest):
    """
    Master Concierge endpoint.
    Accepts a customer message, classifies intent, routes to the correct agent,
    and returns the unified {intent, agent_used, response, staff_action} structure.
    """
    if not req.message.strip():
        raise HTTPException(400, "Message must not be empty")

    result = await process_request(
        message=req.message,
        language=req.language,
        customer_name=req.customer_name,
        session_id=req.session_id,
        staff_utterance=req.staff_utterance,
    )

    return ConciergeResponse(**result)


@router.post("/verify-document")
async def verify_document(
    image: UploadFile = File(...),
    doc_type: str = Form("aadhaar"),
    customer_record: str = Form("{}"),
):
    """
    Document Verification Agent endpoint.
    Accepts an image, runs GPT-4o Vision OCR, returns structured verification JSON.
    """
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, "Unsupported image format. Use JPEG/PNG/WEBP.")

    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        record = json.loads(customer_record)
    except Exception:
        record = {}

    result = await document_verification_agent.verify_from_image(image_b64, doc_type, record)
    return result


@router.post("/verify-document-text")
async def verify_document_text(req: VerifyDocumentTextRequest):
    """
    Document Verification Agent endpoint for OCR text input.
    Returns the same structured verification JSON as image verification.
    """
    if not req.ocr_text.strip():
        raise HTTPException(400, "OCR text must not be empty")

    return await document_verification_agent.verify_from_text(
        ocr_text=req.ocr_text,
        doc_type=req.doc_type,
        customer_record=req.customer_record,
    )


@router.post("/compliance", response_model=ComplianceCheckResponse)
async def compliance_check(req: ComplianceCheckRequest):
    """
    Compliance Monitor Agent endpoint.
    Silently checks a staff utterance for RBI violations.
    """
    result = await compliance_monitor_agent.monitor(req.staff_utterance, req.session_context)
    return ComplianceCheckResponse(**result)


@router.post("/speak")
async def speak(req: TTSRequest):
    """
    Voice Response Agent endpoint.
    Converts text to TTS audio (MP3).
    """
    if not req.text.strip():
        raise HTTPException(400, "Text is empty")

    formatted = voice_response_agent.format_for_voice(req.text, language=req.language)

    audio_bytes = await voice_response_agent.speak(
        text=formatted,
        language=req.language,
        emotion=req.emotion,
        provider=req.provider,
    )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=response.mp3"},
    )


@router.get("/counter-info/{counter_number}")
async def counter_info(counter_number: int):
    """
    Queue Management Agent — get counter details.
    """
    result = await queue_management_agent.get_counter_info(counter_number)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.get("/agents")
async def list_agents():
    """List all available agents and their purposes."""
    return {
        "agents": [
            {
                "name": "CUSTOMER_SERVICE_AGENT",
                "purpose": "Assist customers with general banking questions",
                "handles": ["Account balance", "Debit card issues", "Internet banking", "New account", "General info"],
            },
            {
                "name": "DOCUMENT_VERIFICATION_AGENT",
                "purpose": "Verify customer identity documents during KYC",
                "handles": ["Aadhaar", "PAN", "Passport", "Driving Licence", "Voter ID", "Bank Passbook"],
            },
            {
                "name": "QUEUE_MANAGEMENT_AGENT",
                "purpose": "Manage customer flow — tokens, counters, wait times",
                "handles": ["Token assignment", "Counter direction", "Wait estimation"],
            },
            {
                "name": "COMPLIANCE_MONITOR_AGENT",
                "purpose": "Silently monitor staff for RBI compliance",
                "handles": ["Unauthorized promises", "Loan mis-selling", "Missing KYC", "Suspicious transactions"],
            },
            {
                "name": "VOICE_RESPONSE_AGENT",
                "purpose": "Generate calm, clear voice responses via TTS",
                "handles": ["ElevenLabs TTS", "Sarvam TTS", "Auto-provider selection"],
            },
        ]
    }
