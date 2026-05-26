from __future__ import annotations

from django.db.models import QuerySet

from apps.funds.models import Fund


def list_funds(
    *,
    fund_type: str | None = None,
    category: str | None = None,
    risk_level: int | None = None,
    search: str | None = None,
) -> QuerySet[Fund]:
    qs = Fund.objects.filter(is_active=True)

    if fund_type:
        qs = qs.filter(fund_type=fund_type)
    if category:
        qs = qs.filter(category=category)
    if risk_level is not None:
        qs = qs.filter(risk_level=risk_level)
    if search:
        qs = qs.filter(name__icontains=search)

    return qs
