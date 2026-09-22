from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.ai_profiler.models import PooledQuestion


def claim_pooled_question(*, behaviour: str) -> PooledQuestion | None:
    """Take one pre-generated question for `behaviour`, or None if the pool is dry.

    `skip_locked` rather than a plain lock: two sessions asking for the same
    behaviour at the same moment should get two different questions, not one
    waiting behind the other. Waiting is exactly the latency this exists to
    remove.
    """
    with transaction.atomic():
        pooled = (
            PooledQuestion.objects.select_for_update(skip_locked=True)
            .filter(behaviour=behaviour, claimed_at__isnull=True)
            .order_by("created_at")
            .first()
        )
        if pooled is None:
            return None

        pooled.claimed_at = timezone.now()
        pooled.save(update_fields=["claimed_at", "updated_at"])
        return pooled


def available_counts() -> dict[str, int]:
    """Unclaimed questions per behaviour — what the refill task tops up."""
    from django.db.models import Count

    rows = (
        PooledQuestion.objects.filter(claimed_at__isnull=True)
        .values("behaviour")
        .annotate(total=Count("id"))
    )
    return {row["behaviour"]: row["total"] for row in rows}
