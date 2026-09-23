from __future__ import annotations

import logging

from apps.ai_profiler.selectors.claim_pooled_question import claim_pooled_question
from apps.ai_profiler.services.request_pool_refill import request_pool_refill

logger = logging.getLogger(__name__)


def pooled_payload(*, behaviour: str) -> dict | None:
    """A pre-generated question, shaped like generate_question's output.

    This is the fast path and the one that should almost always hit: one
    indexed row read instead of a call to an LLM. Returning the same dict
    shape as generate_question is what lets next_question treat pooled and
    freshly-generated questions identically.
    """
    pooled = claim_pooled_question(behaviour=behaviour)
    if pooled is None:
        return None

    request_pool_refill()

    return {
        "primary_behaviour": pooled.behaviour,
        "secondary_behaviours": pooled.secondary_behaviours,
        "question": pooled.prompt,
        "subtitle": pooled.subtitle,
        "options": pooled.options,
        "source": pooled.source,
    }
