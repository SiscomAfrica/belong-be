from __future__ import annotations

from uuid import UUID

from apps.common.exceptions import NotFoundError
from apps.funds.models import Fund


def get_fund(*, fund_id: UUID) -> Fund:
    try:
        return Fund.objects.get(pk=fund_id)
    except Fund.DoesNotExist:
        raise NotFoundError("Fund not found")
