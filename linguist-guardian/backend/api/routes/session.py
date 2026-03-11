from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db import get_db
from models.session import Session
from models.transcript import Transcript
from core.gpt4o_client import generate_session_summary
import uuid
from datetime import datetime, timezone

router = APIRouter()


class SessionCreate(BaseModel):
    customer_id: str
    staff_id:    str
    branch_id:   str
    token_number: str


class SessionClose(BaseModel):
    session_id: str


# ── CREATE ──────────────────────────────────────────────
@router.post("/create")
async def create_session(req: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Start a new branch session."""
    session = Session(
        id           = str(uuid.uuid4()),
        customer_id  = req.customer_id,
        staff_id     = req.staff_id,
        branch_id    = req.branch_id,
        token_number = req.token_number,
        status       = "active",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"session_id": session.id, "status": "active"}


# ── GET ─────────────────────────────────────────────────
@router.get("/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    return session


# ── CLOSE + SUMMARIZE ───────────────────────────────────
@router.post("/close")
async def close_session(req: SessionClose, db: AsyncSession = Depends(get_db)):
    """Close session and generate AI summary."""
    result = await db.execute(select(Session).where(Session.id == req.session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    # Fetch transcripts for summary
    t_result = await db.execute(
        select(Transcript).where(Transcript.session_id == req.session_id)
    )
    transcripts = t_result.scalars().all()

    session_data = {
        "session_id":    session.id,
        "customer_id":   session.customer_id,
        "staff_id":      session.staff_id,
        "branch_id":     session.branch_id,
        "token_number":  session.token_number,
        "intent_log":    session.intent_log,
        "actions_taken": session.actions_taken,
        "transcripts": [
            {"speaker": t.speaker, "text": t.raw_text, "intent": t.intent}
            for t in transcripts
        ],
    }

    # Generate summary with GPT-4o
    summary = await generate_session_summary(session_data)

    session.status    = "closed"
    session.summary   = summary
    session.closed_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "closed", "summary": summary}


# ── LOG ACTION ──────────────────────────────────────────
@router.post("/{session_id}/action")
async def log_action(
    session_id: str,
    action: dict,
    db: AsyncSession = Depends(get_db)
):
    """Log a banking action taken during the session."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    actions = list(session.actions_taken or [])
    actions.append({**action, "timestamp": datetime.now(timezone.utc).isoformat()})
    session.actions_taken = actions
    await db.commit()

    return {"status": "logged", "total_actions": len(actions)}


# ── LIST SESSIONS ────────────────────────────────────────
@router.get("/branch/{branch_id}")
async def list_branch_sessions(branch_id: str, db: AsyncSession = Depends(get_db)):
    """Get all sessions for a branch (today)."""
    result = await db.execute(
        select(Session).where(Session.branch_id == branch_id)
        .order_by(Session.created_at.desc())
        .limit(50)
    )
    sessions = result.scalars().all()
    return {"sessions": sessions, "count": len(sessions)}