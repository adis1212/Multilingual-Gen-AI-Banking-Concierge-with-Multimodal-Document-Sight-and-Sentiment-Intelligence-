import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from database.db import get_db
from models.transcript import Transcript
from core.orchestrator import route_conversation, OrchestratorParseError

logger = logging.getLogger(__name__)

router = APIRouter()

FALLBACK_DECISION = {
    "intent": "parse_error",
    "agent": "QUEUE_MANAGEMENT_AGENT",
    "urgency": "medium",
    "recommended_action": "Direct customer to nearest available counter",
}


class OrchestrateRequest(BaseModel):
    transcript: str
    language: str = "en"
    session_id: str | None = None
    sentiment: dict | None = None


class RoutingDecision(BaseModel):
    intent: str
    agent: str
    urgency: str
    recommended_action: str


@router.post("/", response_model=RoutingDecision)
async def orchestrate(req: OrchestrateRequest, db: AsyncSession = Depends(get_db)):
    """Classify customer intent and return a routing decision."""
    if not req.transcript:
        raise HTTPException(status_code=400, detail="transcript must not be empty")

    # Fetch prior context if session_id is provided
    prior_context: list[dict] = []
    if req.session_id:
        try:
            result = await db.execute(
                select(Transcript)
                .where(Transcript.session_id == req.session_id)
                .order_by(desc(Transcript.timestamp))
                .limit(3)
            )
            rows = result.scalars().all()
            prior_context = [
                {
                    "speaker": t.speaker,
                    "text": t.raw_text,
                    "intent": t.intent,
                    "language": t.language,
                }
                for t in reversed(rows)
            ]
        except Exception as exc:
            logger.warning("DB unavailable when fetching prior context: %s", exc)
            prior_context = []

    try:
        decision = await route_conversation(
            transcript=req.transcript,
            language=req.language,
            sentiment=req.sentiment,
            prior_context=prior_context,
        )
        return RoutingDecision(**decision)
    except (OrchestratorParseError, Exception) as exc:
        logger.warning("Orchestrator error, returning fallback: %s", exc)
        return RoutingDecision(**FALLBACK_DECISION)
