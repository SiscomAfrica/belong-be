from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.funds.models import FundPerformance


def get_fund_performance(*, fund_id: UUID) -> QuerySet[FundPerformance]:
    return FundPerformance.objects.filter(
        fund_id=fund_id,
    ).select_related("fund")
