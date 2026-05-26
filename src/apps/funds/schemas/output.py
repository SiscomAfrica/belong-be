from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class FundOut(Schema):
    id: UUID
    name: str
    slug: str
    fund_type: str
    category: str
    risk_level: int
    currency: str
    minimum_investment: Decimal
    projected_annual_return: Decimal
    hero_image_url: str
    is_trending: bool
    is_active: bool


class FundNAVOut(Schema):
    id: UUID
    date: date
    nav_value: Decimal
    daily_change_pct: Decimal


class FundPerformanceOut(Schema):
    id: UUID
    period: str
    return_pct: Decimal
    start_value: Decimal
    end_value: Decimal
    calculated_at: datetime


class FundDetailOut(FundOut):
    description: str
    lock_in_days: int
    effective_annual_yield: Decimal
    annualized_daily_yield: Decimal
    performances: list[FundPerformanceOut]
    created_at: datetime

    @staticmethod
    def resolve_performances(obj):  # noqa: ANN001, ANN205
        return obj.performances.all()


class ProjectionDataPoint(Schema):
    year: int
    value: Decimal
    contributions: Decimal
    earnings: Decimal


class ProjectionOut(Schema):
    data_points: list[ProjectionDataPoint]
    total_contributions: Decimal
    total_earnings: Decimal
    final_value: Decimal


class FundListOut(Schema):
    items: list[FundOut]
    count: int
