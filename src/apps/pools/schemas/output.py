from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema

from apps.pools.models import Pool


class PoolOut(Schema):
    id: UUID
    fund_id: UUID
    fund_name: str
    total_units: Decimal
    total_aum: Decimal
    nav_per_unit: Decimal
    underlying: list
    updated_at: datetime

    @staticmethod
    def resolve_fund_name(obj: Pool) -> str:
        return obj.fund.name


class PoolListOut(Schema):
    items: list[PoolOut]
    count: int
