from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from apps.investments.selectors.list_user_holdings import list_user_holdings


def get_portfolio_summary(*, user_id: UUID) -> dict:
    holdings = list_user_holdings(user_id=user_id)

    total_value = Decimal("0")
    total_invested = Decimal("0")
    count = 0

    for h in holdings:
        total_value += getattr(h, "current_value", Decimal("0"))
        total_invested += h.total_invested
        count += 1

    total_gain = total_value - total_invested
    gain_pct = (
        (total_gain / total_invested * 100) if total_invested else Decimal("0")
    )

    from apps.investments.models import PortfolioSnapshot

    snapshot = (
        PortfolioSnapshot.objects.filter(user_id=user_id)
        .order_by("-date")
        .first()
    )

    return {
        "total_value": total_value,
        "total_invested": total_invested,
        "total_gain": total_gain,
        "gain_pct": gain_pct,
        "holdings_count": count,
        "daily_change": snapshot.daily_change if snapshot else Decimal("0"),
        "daily_change_pct": snapshot.daily_change_pct if snapshot else Decimal("0"),
    }
