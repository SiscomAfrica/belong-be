from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.selectors.get_session_signals import get_session_signals
from apps.ai_profiler.services.assess_coverage import next_behaviour_to_probe

BASE_QUESTIONS = 4


def target_behaviour(*, asked: list, session_id: UUID) -> str | None:
    """Which behaviour the next question should lead on, or None when done.

    Inside the base set and past it, the answer comes from the same place —
    the first behaviour the session has not measured yet. The distinction the
    branch preserves is what None *means*: before the base set is exhausted it
    says everything was covered early, after it that no genuine gap is left to
    justify asking again.
    """
    signals = get_session_signals(session_id=session_id)

    if len(asked) < BASE_QUESTIONS:
        pending = next_behaviour_to_probe(signals=signals)
        if pending:
            return pending
        # Everything already covered before the base set is exhausted.
        return None

    # Past the base set, only a genuine coverage gap justifies another question.
    return next_behaviour_to_probe(signals=signals)
