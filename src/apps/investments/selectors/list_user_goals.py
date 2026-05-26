from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.db.models import QuerySet, Subquery, OuterRef, DecimalField
from django.db.models.functions import Coalesce

from apps.investments.models.holding import Holding
from apps.investments.models.investment_goal import InvestmentGoal


def list_user_goals(*, user_id: UUID) -> QuerySet[InvestmentGoal]:
    holding_value = Holding.objects.filter(
        user_id=user_id, fund_id=OuterRef("fund_id")
    ).values("total_invested")[:1]

    return (
        InvestmentGoal.objects.filter(user_id=user_id)
        .select_related("fund")
        .annotate(
            current_value=Coalesce(
                Subquery(holding_value, output_field=DecimalField()),
                Decimal("0"),
            )
        )
    )
