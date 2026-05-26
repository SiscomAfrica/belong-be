from __future__ import annotations

from uuid import UUID

from apps.pools.exceptions import PoolNotFoundError
from apps.pools.models import Pool


def get_pool(*, fund_id: UUID) -> Pool:
    try:
        return Pool.objects.select_related("fund").get(fund_id=fund_id)
    except Pool.DoesNotExist:
        raise PoolNotFoundError()
