from __future__ import annotations

from uuid import UUID

from apps.funds.models import FundNAV


def get_latest_fund_nav(*, fund_id: UUID) -> FundNAV | None:
    return (
        FundNAV.objects.filter(fund_id=fund_id)
        .order_by("-date")
        .first()
    )
