from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import SessionAlreadyCompletedError, SessionNotFoundError
from apps.ai_profiler.models import ConversationSession, InvestorProfile, SessionStatus
from apps.ai_profiler.services.complete_legacy_session import complete_legacy_session
from apps.ai_profiler.services.complete_rubric_session import complete_rubric_session


def complete_session(*, session_id: UUID, user_id: UUID) -> InvestorProfile:
    """Score a finished profiling session and assign an investor profile.

    Which path applies is decided by what the session actually contains, not by
    a version header the client controls: a session with generated questions is
    scored against the rubric, one without came from a client that predates
    them and keeps the behaviour it already had.
    """
    session = _active_session(session_id=session_id, user_id=user_id)

    if _has_generated_questions(session=session):
        return complete_rubric_session(session=session, user_id=user_id)

    return complete_legacy_session(session=session, user_id=user_id)


def _has_generated_questions(*, session: ConversationSession) -> bool:
    return session.questions.filter(superseded_at=None).exists()


def _active_session(*, session_id: UUID, user_id: UUID) -> ConversationSession:
    try:
        session = ConversationSession.objects.get(id=session_id, user_id=user_id)
    except ConversationSession.DoesNotExist:
        raise SessionNotFoundError() from None

    if session.status != SessionStatus.ACTIVE:
        raise SessionAlreadyCompletedError()

    return session
