from __future__ import annotations

import logging

from apps.ai_profiler.services.fallback_questions import fallback_for

logger = logging.getLogger(__name__)


def banked_payload(*, behaviour: str) -> dict | None:
    """The shipped question for `behaviour`, shaped like generate_question's output.

    Read from a cached fixture, so this cannot block, time out, or cost money.
    That is the whole reason it exists: it is what the request path reaches for
    when the pool is dry, in place of an LLM call the user would have to wait
    out.

    Banked questions carry the same anchors as generated ones, so a user served
    from here is graded on exactly the same scale. The bank costs variety,
    never fairness.
    """
    banked = fallback_for(behaviour=behaviour)
    if banked is None:
        return None

    return {**banked, "source": "fallback"}
