from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import SessionAlreadyCompletedError, SessionNotFoundError
from apps.ai_profiler.models import ConversationSession, SessionStatus


def get_active_session(*, session_id: UUID, user_id: UUID) -> ConversationSession:
    """The session, provided it belongs to this user and is still open.

    Scoped by user_id rather than fetched by primary key alone: a session id
    is the only thing standing between one user's profiling run and another's.
    """
    try:
        session = ConversationSession.objects.get(id=session_id, user_id=user_id)
    except ConversationSession.DoesNotExist:
        raise SessionNotFoundError() from None

    if session.status != SessionStatus.ACTIVE:
        raise SessionAlreadyCompletedError()

    return session
