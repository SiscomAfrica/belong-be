from __future__ import annotations

from uuid import UUID

from apps.payments.models import StandingOrder, StandingOrderStatus

_LIVE = (StandingOrderStatus.PENDING, StandingOrderStatus.ACTIVE)


def has_live_standing_order(*, plan_id: UUID) -> bool:
    """True when Safaricom may still deduct against this plan."""
    return StandingOrder.objects.filter(
        recurring_plan_id=plan_id, status__in=_LIVE,
    ).exists()
