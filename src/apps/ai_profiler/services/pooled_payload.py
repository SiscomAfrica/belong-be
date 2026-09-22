from __future__ import annotations

import logging

from django.db import transaction

from apps.ai_profiler.selectors.claim_pooled_question import claim_pooled_question

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

    _request_refill()

    return {
        "primary_behaviour": pooled.behaviour,
        "secondary_behaviours": pooled.secondary_behaviours,
        "question": pooled.prompt,
        "subtitle": pooled.subtitle,
        "options": pooled.options,
        "source": pooled.source,
    }


def _request_refill() -> None:
    """Ask for a top-up after taking one, rather than waiting for the beat.

    Queued on commit: a worker that picks the task up before this claim is
    committed would count the row it is replacing as still available and
    generate nothing.

    Non-fatal by design. The question has already been served; a broker that
    is down must not turn a successful read into a failed request, and the
    scheduled refill will catch up.
    """
    from apps.ai_profiler.tasks.refill_question_pool import refill_question_pool

    def enqueue() -> None:
        try:
            refill_question_pool.delay()
        except Exception:
            logger.exception("Could not queue question pool refill")

    transaction.on_commit(enqueue)
