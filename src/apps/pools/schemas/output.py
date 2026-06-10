from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.pools.models import Pool


class PoolOut(Schema):
    id: UUID = Field(description="Pool identifier")
    fund_id: UUID = Field(description="Associated fund UUID")
    fund_name: str = Field(description="Associated fund display name")
    total_units: Decimal = Field(description="Total units outstanding in the pool")
    total_aum: Decimal = Field(description="Total assets under management in KES")
    nav_per_unit: Decimal = Field(description="Current NAV per unit")
    underlying: list = Field(description="Underlying asset allocation breakdown")
    updated_at: datetime = Field(description="Last NAV update timestamp")

    @staticmethod
    def resolve_fund_name(obj: Pool) -> str:
        return obj.fund.name


class PoolListOut(Schema):
    items: list[PoolOut] = Field(description="List of investment pools")
    count: int = Field(description="Total number of pools")
