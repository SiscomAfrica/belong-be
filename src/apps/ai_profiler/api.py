from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.ai_profiler.schemas import (
    InvestorProfileOut,
    MessageIn,
    MessageOut,
    SessionDetailOut,
    SessionListOut,
    SessionOut,
)
from apps.ai_profiler.selectors.get_investor_profile import get_investor_profile
from apps.ai_profiler.selectors.get_session import get_session
from apps.ai_profiler.selectors.list_user_sessions import list_user_sessions
from apps.ai_profiler.services.complete_session import complete_session
from apps.ai_profiler.services.send_message import send_message
from apps.ai_profiler.services.start_session import start_session

profiler_router = Router(tags=["ai-profiler"])


@profiler_router.post("/sessions/start", response={201: SessionOut})
def start_session_endpoint(request):
    """Start a new AI profiler conversation session."""
    session = start_session(user_id=request.auth.id)
    return 201, session


@profiler_router.post("/sessions/{session_id}/message", response=MessageOut)
def send_message_endpoint(request, session_id: UUID, payload: MessageIn):
    """Send a message to the AI profiler and receive a response."""
    return send_message(session_id=session_id, user_id=request.auth.id, content=payload.content)


@profiler_router.post("/sessions/{session_id}/complete", response=InvestorProfileOut)
def complete_session_endpoint(request, session_id: UUID):
    """Complete the profiler session and generate the investor profile."""
    return complete_session(session_id=session_id, user_id=request.auth.id)


@profiler_router.get("/sessions", response=SessionListOut)
def list_sessions_endpoint(request):
    """List all profiler sessions for the authenticated user."""
    sessions = list_user_sessions(user_id=request.auth.id)
    return SessionListOut(items=list(sessions), count=sessions.count())


@profiler_router.get("/sessions/{session_id}", response=SessionDetailOut)
def get_session_endpoint(request, session_id: UUID):
    """Return session details with full message history."""
    return get_session(session_id=session_id, user_id=request.auth.id)


@profiler_router.get("/profile", response=InvestorProfileOut)
def get_profile_endpoint(request):
    """Return the user's AI-generated investor profile."""
    return get_investor_profile(user_id=request.auth.id)
