from __future__ import annotations

from uuid import UUID

from apps.common.exceptions import NotFoundError
from apps.investments.models import Investment


def get_investment(*, investment_id: UUID, user_id: UUID) -> Investment:
    try:
        return Investment.objects.select_related("fund").get(
            id=investment_id, user_id=user_id
        )
    except Investment.DoesNotExist:
        raise NotFoundError("Investment not found.")
