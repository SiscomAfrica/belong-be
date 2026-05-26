from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.utils import timezone

from apps.investments.models import PortfolioSnapshot
from apps.investments.selectors.list_user_holdings import list_user_holdings


def record_portfolio_snapshot(*, user_id: UUID) -> PortfolioSnapshot:
    today = timezone.now().date()
    holdings = list_user_holdings(user_id=user_id)

    total_value = Decimal("0")
    total_invested = Decimal("0")
    for h in holdings:
        total_value += getattr(h, "current_value", Decimal("0"))
        total_invested += h.total_invested

    yesterday = (
        PortfolioSnapshot.objects.filter(user_id=user_id, date__lt=today)
        .order_by("-date")
        .first()
    )

    daily_change = Decimal("0")
    daily_change_pct = Decimal("0")
    if yesterday and yesterday.total_value:
        daily_change = total_value - yesterday.total_value
        daily_change_pct = (daily_change / yesterday.total_value) * 100

    snapshot, _ = PortfolioSnapshot.objects.update_or_create(
        user_id=user_id,
        date=today,
        defaults={
            "total_value": total_value,
            "total_invested": total_invested,
            "daily_change": daily_change,
            "daily_change_pct": daily_change_pct,
        },
    )

    return snapshot
