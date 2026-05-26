from __future__ import annotations

from uuid import UUID

from apps.common.exceptions import NotFoundError
from apps.investments.models import Holding


def get_holding(*, user_id: UUID, fund_id: UUID) -> Holding:
    try:
        return Holding.objects.select_related("fund").get(
            user_id=user_id, fund_id=fund_id
        )
    except Holding.DoesNotExist:
        raise NotFoundError("Holding not found.")
