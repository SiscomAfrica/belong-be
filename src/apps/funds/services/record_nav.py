from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from apps.funds.models import FundNAV


def record_nav(
    *,
    fund_id: UUID,
    date: date,
    nav_value: Decimal,
    daily_change_pct: Decimal,
) -> FundNAV:
    nav, _created = FundNAV.objects.update_or_create(
        fund_id=fund_id,
        date=date,
        defaults={
            "nav_value": nav_value,
            "daily_change_pct": daily_change_pct,
        },
    )
    return nav
