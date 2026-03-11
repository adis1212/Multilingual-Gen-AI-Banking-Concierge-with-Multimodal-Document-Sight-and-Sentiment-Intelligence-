from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.gpt4o_client import extract_intent, check_compliance

router = APIRouter()


class IntentRequest(BaseModel):
    transcript: str
    language: str = "mr"
    customer_context: dict = {}
    session_id: str = ""


class ComplianceRequest(BaseModel):
    staff_utterance: str
    session_id: str = ""


@router.post("/extract")
async def get_intent(req: IntentRequest):
    """Extract customer intent + generate staff advisory."""
    if not req.transcript.strip():
        raise HTTPException(400, "Transcript is empty")

    result = await extract_intent(req.transcript, req.language, req.customer_context)
    return result


@router.post("/compliance")
async def compliance_check(req: ComplianceRequest):
    """Silent RBI compliance check on staff utterance."""
    if not req.staff_utterance.strip():
        return {"compliant": True, "violations": [], "warning_message": "", "severity": "none"}

    result = await check_compliance(req.staff_utterance)
    return result