from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings

from apps.ai_profiler.exceptions import ProviderRateLimitedError
from apps.ai_profiler.models import PooledQuestion
from apps.ai_profiler.rubric import BEHAVIOUR_KEYS
from apps.ai_profiler.selectors.claim_pooled_question import available_counts
from apps.ai_profiler.services.generate_question import generate_question
from apps.ai_profiler.services.provider_cooldown import (
    provider_is_cooling_down,
    start_provider_cooldown,
)

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
    if provider_is_cooling_down():
        logger.info("Question pool refill skipped: provider still rate limited")
        return 0

    wanted = target or getattr(
        settings, "QUESTION_POOL_TARGET", TARGET_PER_BEHAVIOUR,
    )
    counts = available_counts()
    created = 0

    for behaviour in BEHAVIOUR_KEYS:
        shortfall = wanted - counts.get(behaviour, 0)
        for _ in range(max(shortfall, 0)):
            try:
                if _store_one(behaviour=behaviour):
                    created += 1
            except ProviderRateLimitedError as exc:
                # Abandon the whole run, not just this behaviour. The limit is
                # on the account, so the remaining behaviours would only meet
                # the same refusal.
                start_provider_cooldown(seconds=exc.retry_after)
                logger.warning(
                    "Question pool refill stopped: provider rate limited "
                    "(%s created before stopping)", created,
                )
                return created

    logger.info("Question pool refilled: %s created", created)
    return created


def _store_one(*, behaviour: str) -> bool:
    """Returns whether a question was banked. Lets a rate limit propagate."""
    try:
        generated = generate_question(behaviour=behaviour, asked=[])
    except ProviderRateLimitedError:
        raise
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
