from __future__ import annotations

import logging
from uuid import UUID

from apps.ai_profiler.models import QuestionSource, SessionQuestion
from apps.ai_profiler.selectors.get_active_session import get_active_session
from apps.ai_profiler.selectors.get_session_questions import (
    active_questions,
    next_position,
)
from apps.ai_profiler.services.banked_payload import banked_payload
from apps.ai_profiler.services.pooled_payload import pooled_payload
from apps.ai_profiler.services.request_pool_refill import request_pool_refill
from apps.ai_profiler.services.target_behaviour import BASE_QUESTIONS, target_behaviour

logger = logging.getLogger(__name__)

__all__ = ["BASE_QUESTIONS", "MAX_QUESTIONS", "next_question"]

MAX_QUESTIONS = 5


def next_question(*, session_id: UUID, user_id: UUID) -> SessionQuestion | None:
    """The next question to put to the user, or None when we have enough.

    Returns None once every behaviour is covered, or once the hard cap is
    reached. The cap exists so a user is never held in onboarding by a
    behaviour the generator keeps failing to measure.
    """
    session = get_active_session(session_id=session_id, user_id=user_id)
    asked = active_questions(session_id=session_id)

    if len(asked) >= MAX_QUESTIONS:
        return None

    behaviour = target_behaviour(asked=asked, session_id=session_id)
    if behaviour is None:
        return None

    generated = pooled_payload(behaviour=behaviour)

    if generated is None:
        # Pool was dry. This path serves the bank and returns; it never calls
        # the generator.
        #
        # Generating here used to be the fallback, and it is the one thing
        # this request cannot afford. LLM_GENERATION_RETRIES + 1 attempts at
        # LLM_GENERATION_TIMEOUT each is up to a minute of a user sitting on
        # a tapped Continue button — longer than the mobile client's own
        # 30s timeout, so the app gives up while the server is still trying
        # and the user sees a hang rather than a question.
        #
        # So: availability over freshness. A banked question is less varied
        # than a generated one but carries the same anchors, so it grades
        # identically — the user loses novelty, never correctness. The
        # refill is asked for asynchronously, which means the pool heals for
        # whoever comes next while this user is already reading.
        generated = banked_payload(behaviour=behaviour)
        if generated is None:
            # Nothing pooled and nothing banked. Better to leave the
            # behaviour imputed — and say so on the profile — than hold the
            # user in onboarding.
            logger.error("No question for %s; leaving it unmeasured", behaviour)
            return None

        logger.warning("Question pool dry for %s; served from the bank", behaviour)
        request_pool_refill()

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
