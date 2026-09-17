from __future__ import annotations

from apps.payments.models import StandingOrder

NO_STANDING_ORDER = "NONE"


def get_plan_standing_order_status(*, plan) -> str:
    """Status of the standing order funding a plan, or NONE.

    Reads a prefetched `standing_orders` cache when the caller supplied one —
    serialising a list of plans otherwise issues a query per row.
    """
    cached = getattr(plan, "_prefetched_objects_cache", {}).get("standing_orders")
    if cached is not None:
        orders = list(cached)
        return orders[0].status if orders else NO_STANDING_ORDER

    status = (
        StandingOrder.objects.filter(recurring_plan_id=plan.id)
        .order_by("-created_at")
        .values_list("status", flat=True)
        .first()
    )
    return status or NO_STANDING_ORDER
