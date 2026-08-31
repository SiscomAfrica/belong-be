from __future__ import annotations

import logging
from uuid import UUID

from apps.ai_profiler.exceptions import SessionAlreadyCompletedError, SessionNotFoundError
from apps.ai_profiler.models import (
    ConversationSession,
    QuestionSource,
    SessionQuestion,
    SessionStatus,
)
from apps.ai_profiler.selectors.get_session_questions import (
    active_questions,
    next_position,
)
from apps.ai_profiler.selectors.get_session_signals import get_session_signals
from apps.ai_profiler.services.assess_coverage import next_behaviour_to_probe
from apps.ai_profiler.services.generate_question import generate_question

logger = logging.getLogger(__name__)

BASE_QUESTIONS = 4
MAX_QUESTIONS = 5


def next_question(*, session_id: UUID, user_id: UUID) -> SessionQuestion | None:
    """The next question to put to the user, or None when we have enough.

    Returns None once every behaviour is covered, or once the hard cap is
    reached. The cap exists so a user is never held in onboarding by a
    behaviour the generator keeps failing to measure.
    """
    session = _active_session(session_id=session_id, user_id=user_id)
    asked = active_questions(session_id=session_id)

    if len(asked) >= MAX_QUESTIONS:
        return None

    behaviour = _target_behaviour(asked=asked, session_id=session_id)
    if behaviour is None:
        return None

    try:
        generated = generate_question(
            behaviour=behaviour,
            asked=[{"question": q.prompt} for q in asked],
        )
    except LookupError:
        # Nothing generated and nothing banked for this behaviour. Better to
        # score with it imputed — and say so on the profile — than to hold the
        # user in onboarding with no question we can actually ask.
        logger.exception("No question available for %s; leaving it unmeasured", behaviour)
        return None

    return SessionQuestion.objects.create(
        session=session,
        position=next_position(session_id=session_id),
        primary_behaviour=generated["primary_behaviour"],
        secondary_behaviours=generated.get("secondary_behaviours", []),
        source=(
            QuestionSource.FALLBACK
            if generated.get("source") == "fallback"
            else QuestionSource.GENERATED
        ),
        prompt=generated["question"],
        subtitle=generated.get("subtitle", ""),
        options=generated["options"],
    )


def _target_behaviour(*, asked: list, session_id: UUID) -> str | None:
    """Which behaviour the next question should lead on."""
    if len(asked) < BASE_QUESTIONS:
        pending = next_behaviour_to_probe(
            signals=get_session_signals(session_id=session_id),
        )
        if pending:
            return pending
        # Everything already covered before the base set is exhausted.
        return None

    # Past the base set, only a genuine coverage gap justifies another question.
    return next_behaviour_to_probe(signals=get_session_signals(session_id=session_id))


def _active_session(*, session_id: UUID, user_id: UUID) -> ConversationSession:
    try:
        session = ConversationSession.objects.get(id=session_id, user_id=user_id)
    except ConversationSession.DoesNotExist:
        raise SessionNotFoundError() from None

    if session.status != SessionStatus.ACTIVE:
        raise SessionAlreadyCompletedError()

    return session
