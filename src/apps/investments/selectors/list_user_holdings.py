from __future__ import annotations

from uuid import UUID

from django.db.models import DecimalField, F, OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce

from apps.funds.models import FundNAV
from apps.investments.models import Holding


def list_user_holdings(*, user_id: UUID) -> QuerySet[Holding]:
    latest_nav = (
        FundNAV.objects.filter(fund_id=OuterRef("fund_id"))
        .order_by("-date")
        .values("nav_value")[:1]
    )

    return (
        Holding.objects.filter(user_id=user_id)
        .select_related("fund")
        .annotate(
            _latest_nav=Subquery(latest_nav, output_field=DecimalField()),
            current_value=Coalesce(
                F("_latest_nav") * F("total_units"),
                0,
                output_field=DecimalField(),
            ),
        )
    )
