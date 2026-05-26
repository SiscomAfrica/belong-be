from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class InvestmentFundOut(Schema):
    id: UUID
    name: str
    slug: str
    currency: str


class InvestmentOut(Schema):
    id: UUID
    fund: InvestmentFundOut
    amount: Decimal
    units: Decimal
    nav_at_purchase: Decimal
    status: str
    idempotency_key: str
    confirmed_at: datetime | None
    created_at: datetime


class InvestmentListOut(Schema):
    items: list[InvestmentOut]
    count: int


class HoldingFundOut(Schema):
    id: UUID
    name: str
    slug: str
    currency: str
    hero_image_url: str
    risk_level: int


class HoldingOut(Schema):
    id: UUID
    fund: HoldingFundOut
    total_units: Decimal
    total_invested: Decimal
    average_nav: Decimal
    current_value: Decimal
    unrealized_gain: Decimal
    gain_pct: Decimal

    @staticmethod
    def resolve_current_value(obj) -> Decimal:  # noqa: ANN001
        return getattr(obj, "current_value", Decimal("0"))

    @staticmethod
    def resolve_unrealized_gain(obj) -> Decimal:  # noqa: ANN001
        current = getattr(obj, "current_value", Decimal("0"))
        return current - obj.total_invested

    @staticmethod
    def resolve_gain_pct(obj) -> Decimal:  # noqa: ANN001
        current = getattr(obj, "current_value", Decimal("0"))
        if obj.total_invested == 0:
            return Decimal("0")
        return ((current - obj.total_invested) / obj.total_invested) * 100


class HoldingDetailOut(HoldingOut):
    investments: list[InvestmentOut]

    @staticmethod
    def resolve_investments(obj):  # noqa: ANN001, ANN205
        return obj.fund.investments.filter(
            user_id=obj.user_id, status="CONFIRMED"
        ).select_related("fund")


class PortfolioSummaryOut(Schema):
    total_value: Decimal
    total_invested: Decimal
    total_gain: Decimal
    gain_pct: Decimal
    holdings_count: int
    daily_change: Decimal
    daily_change_pct: Decimal


class PortfolioSnapshotOut(Schema):
    date: date
    total_value: Decimal
    total_invested: Decimal
    daily_change: Decimal
    daily_change_pct: Decimal
