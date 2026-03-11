from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter()

# All connected staff clients per session
connected_clients: Dict[str, List[WebSocket]] = {}


@router.websocket("/events/{session_id}")
async def session_events(websocket: WebSocket, session_id: str):
    """
    Real-time session event broadcaster.
    Used to push alerts, intent updates, sentiment changes to the frontend.
    """
    await websocket.accept()

    if session_id not in connected_clients:
        connected_clients[session_id] = []
    connected_clients[session_id].append(websocket)

    print(f"📡 Event client connected: {session_id} ({len(connected_clients[session_id])} total)")

    try:
        while True:
            # Keep connection alive, listen for pings
            data = await websocket.receive_text()
            payload = json.loads(data)

            if payload.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        connected_clients[session_id].remove(websocket)
        if not connected_clients[session_id]:
            del connected_clients[session_id]
        print(f"📡 Event client disconnected: {session_id}")


async def broadcast_event(session_id: str, event: dict):
    """
    Push an event to all connected clients for a session.
    Call this from any backend route to push real-time updates.
    """
    if session_id not in connected_clients:
        return

    dead = []
    for ws in connected_clients[session_id]:
        try:
            await ws.send_text(json.dumps(event))
        except Exception:
            dead.append(ws)

    for ws in dead:
        connected_clients[session_id].remove(ws)


# ── Event helpers ────────────────────────────────────────

async def push_intent_alert(session_id: str, intent: dict):
    await broadcast_event(session_id, {"type": "intent_update", "data": intent})

async def push_sentiment_alert(session_id: str, sentiment: dict):
    await broadcast_event(session_id, {"type": "sentiment_update", "data": sentiment})

async def push_critical_alert(session_id: str, message: str):
    await broadcast_event(session_id, {"type": "critical_alert", "message": message})

async def push_ocr_result(session_id: str, result: dict):
    await broadcast_event(session_id, {"type": "ocr_result", "data": result})