from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings

from apps.ai_profiler.models import PooledQuestion
from apps.ai_profiler.rubric import BEHAVIOUR_KEYS
from apps.ai_profiler.selectors.claim_pooled_question import available_counts
from apps.ai_profiler.services.generate_question import generate_question

logger = logging.getLogger(__name__)

# Enough that a burst of sign-ups cannot drain a behaviour between refills,
# small enough that questions do not go stale sitting in the pool.
TARGET_PER_BEHAVIOUR = 5


@shared_task(
    bind=True,
    name="apps.ai_profiler.tasks.refill_question_pool",
    max_retries=2,
    default_retry_delay=60,
    retry_backoff=True,
    retry_jitter=True,
)
def refill_question_pool(self, target: int | None = None) -> int:
    """Top every behaviour back up to `target` unclaimed questions.

    Idempotent: it counts what is there and generates the difference, so a
    duplicate run is a no-op rather than a double fill.

    A generation failure for one behaviour must not abandon the rest — each is
    independent, and a half-full pool still serves instantly.
    """
    wanted = target or getattr(
        settings, "QUESTION_POOL_TARGET", TARGET_PER_BEHAVIOUR,
    )
    counts = available_counts()
    created = 0

    for behaviour in BEHAVIOUR_KEYS:
        shortfall = wanted - counts.get(behaviour, 0)
        for _ in range(max(shortfall, 0)):
            if _store_one(behaviour=behaviour):
                created += 1

    logger.info("Question pool refilled: %s created", created)
    return created


def _store_one(*, behaviour: str) -> bool:
    try:
        generated = generate_question(behaviour=behaviour, asked=[])
    except Exception:
        logger.exception("Pool generation failed for %s", behaviour)
        return False

    # A banked fallback is already served instantly from disk, so storing one
    # here would spend a pool slot on something the fallback path covers for
    # free — and would crowd out a real generated question.
    if generated.get("source") == "fallback":
        return False

    PooledQuestion.objects.create(
        behaviour=generated["primary_behaviour"],
        prompt=generated["question"],
        subtitle=generated.get("subtitle", ""),
        options=generated["options"],
        secondary_behaviours=generated.get("secondary_behaviours", []),
    )
    return True
