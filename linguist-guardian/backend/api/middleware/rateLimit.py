from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

# Simple in-memory rate limiter
# Production: use Redis
_request_counts: dict = defaultdict(list)
RATE_LIMIT  = 60        # requests
WINDOW_SECS = 60        # per minute

# Higher limits for audio/streaming endpoints
AUDIO_LIMIT = 200


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now       = datetime.utcnow()
    window    = now - timedelta(seconds=WINDOW_SECS)

    # Clean old entries
    _request_counts[client_ip] = [
        t for t in _request_counts[client_ip] if t > window
    ]

    # Check limit
    limit = AUDIO_LIMIT if "audio" in request.url.path else RATE_LIMIT
    if len(_request_counts[client_ip]) >= limit:
        raise HTTPException(
            429,
            detail=f"Rate limit exceeded. Max {limit} requests per minute."
        )

    _request_counts[client_ip].append(now)
    return await call_next(request)