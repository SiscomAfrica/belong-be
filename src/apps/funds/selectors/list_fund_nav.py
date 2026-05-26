from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.db.models import QuerySet
from django.utils import timezone

from apps.funds.models import FundNAV


def list_fund_nav(*, fund_id: UUID, days: int = 30) -> QuerySet[FundNAV]:
    since = (timezone.now() - timedelta(days=days)).date()
    return (
        FundNAV.objects.filter(fund_id=fund_id, date__gte=since)
        .select_related("fund")
        .order_by("-date")
    )
