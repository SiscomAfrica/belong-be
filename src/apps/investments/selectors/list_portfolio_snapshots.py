from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.db.models import QuerySet
from django.utils import timezone

from apps.investments.models import PortfolioSnapshot


def list_portfolio_snapshots(
    *, user_id: UUID, days: int = 30
) -> QuerySet[PortfolioSnapshot]:
    start_date = timezone.now().date() - timedelta(days=days)

    return (
        PortfolioSnapshot.objects.filter(user_id=user_id, date__gte=start_date)
        .order_by("date")
    )
