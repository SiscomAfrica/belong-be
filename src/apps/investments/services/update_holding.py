from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.db import transaction

from apps.investments.models import Holding


def update_holding(
    *, user_id: UUID, fund_id: UUID, units: Decimal, amount: Decimal
) -> Holding:
    with transaction.atomic():
        holding, _ = Holding.objects.select_for_update().get_or_create(
            user_id=user_id,
            fund_id=fund_id,
            defaults={"total_units": 0, "total_invested": 0, "average_nav": 0},
        )
        holding.total_units += units
        holding.total_invested += amount

        if holding.total_units > 0:
            holding.average_nav = holding.total_invested / holding.total_units

        holding.save(update_fields=["total_units", "total_invested", "average_nav", "updated_at"])

    return holding
