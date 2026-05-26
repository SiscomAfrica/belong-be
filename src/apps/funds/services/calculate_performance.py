from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.utils import timezone

from apps.funds.models import FundNAV, FundPerformance
from apps.funds.models.fund_performance import PerformancePeriod
from apps.funds.selectors.get_fund import get_fund

PERIOD_DAYS: dict[str, int] = {
    PerformancePeriod.ONE_MONTH: 30,
    PerformancePeriod.THREE_MONTHS: 90,
    PerformancePeriod.SIX_MONTHS: 180,
    PerformancePeriod.ONE_YEAR: 365,
    PerformancePeriod.FIVE_YEARS: 1825,
}


def calculate_performance(*, fund_id: UUID) -> list[FundPerformance]:
    fund = get_fund(fund_id=fund_id)
    now = timezone.now()
    results: list[FundPerformance] = []

    for period, days in PERIOD_DAYS.items():
        start_date = (now - timedelta(days=days)).date()
        navs = FundNAV.objects.filter(
            fund=fund,
            date__gte=start_date,
        ).order_by("date")

        if navs.count() < 2:
            continue

        start_nav = navs.first()
        end_nav = navs.last()
        start_val = start_nav.nav_value
        end_val = end_nav.nav_value
        return_pct = ((end_val - start_val) / start_val) * 100

        perf, _ = FundPerformance.objects.update_or_create(
            fund=fund,
            period=period,
            defaults={
                "return_pct": return_pct,
                "start_value": start_val,
                "end_value": end_val,
                "calculated_at": now,
            },
        )
        results.append(perf)

    return results
