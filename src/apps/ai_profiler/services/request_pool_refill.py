from __future__ import annotations

import logging

from django.db import transaction

logger = logging.getLogger(__name__)


def request_pool_refill() -> None:
    """Ask for a top-up after taking from the pool, rather than waiting for the beat.

    Queued on commit: a worker that picks the task up before the claim is
    committed would count the row it is replacing as still available and
    generate nothing.

    Non-fatal by design. Whatever prompted the refill has already been served;
    a broker that is down must not turn a successful read into a failed
    request, and the scheduled refill will catch up.
    """
    from apps.ai_profiler.tasks.refill_question_pool import refill_question_pool

    def enqueue() -> None:
        try:
            refill_question_pool.delay()
        except Exception:
            logger.exception("Could not queue question pool refill")

    transaction.on_commit(enqueue)
