from __future__ import annotations

import datetime as dt

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class InvestmentFundOut(Schema):
    id: UUID = Field(description="Fund identifier")
    name: str = Field(description="Fund display name")
    slug: str = Field(description="URL-safe fund slug")
    currency: str = Field(description="Fund denomination currency")


class InvestmentOut(Schema):
    id: UUID = Field(description="Investment identifier")
    fund: InvestmentFundOut = Field(description="Fund summary")
    amount: Decimal = Field(description="Invested amount in KES")
    units: Decimal = Field(description="Number of fund units allocated")
    nav_at_purchase: Decimal = Field(description="NAV per unit at time of purchase")
    status: str = Field(description="Status: PENDING | CONFIRMED | FAILED | CANCELLED")
    idempotency_key: str = Field(description="Client-provided idempotency key")
    confirmed_at: datetime | None = Field(default=None, description="When the investment was confirmed")
    created_at: datetime = Field(description="Investment creation timestamp")


class InvestmentListOut(Schema):
    items: list[InvestmentOut] = Field(description="List of investments")
    count: int = Field(description="Total number of matching investments")


class HoldingFundOut(Schema):
    id: UUID = Field(description="Fund identifier")
    name: str = Field(description="Fund display name")
    slug: str = Field(description="URL-safe fund slug")
    currency: str = Field(description="Fund denomination currency")
    hero_image_url: str = Field(description="Card hero image URL")
    risk_level: int = Field(description="Risk level 1-5")


class HoldingOut(Schema):
    id: UUID = Field(description="Holding record identifier")
    fund: HoldingFundOut = Field(description="Fund summary")
    total_units: Decimal = Field(description="Total units held in this fund")
    total_invested: Decimal = Field(description="Total amount invested in KES")
    average_nav: Decimal = Field(description="Weighted average NAV at purchase")
    current_value: Decimal = Field(description="Current market value in KES")
    unrealized_gain: Decimal = Field(description="Unrealized profit/loss in KES")
    gain_pct: Decimal = Field(description="Unrealized gain as a percentage")

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
    investments: list[InvestmentOut] = Field(description="Individual confirmed investments in this holding")

    @staticmethod
    def resolve_investments(obj):  # noqa: ANN001, ANN205
        return obj.fund.investments.filter(
            user_id=obj.user_id, status="CONFIRMED"
        ).select_related("fund")


class PortfolioSummaryOut(Schema):
    total_value: Decimal = Field(description="Total portfolio market value in KES")
    total_invested: Decimal = Field(description="Total amount invested in KES")
    total_gain: Decimal = Field(description="Total unrealized gain/loss in KES")
    gain_pct: Decimal = Field(description="Total gain as a percentage")
    holdings_count: int = Field(description="Number of distinct fund holdings")
    daily_change: Decimal = Field(description="Day-over-day value change in KES")
    daily_change_pct: Decimal = Field(description="Day-over-day change percentage")


class PortfolioSnapshotOut(Schema):
    date: dt.date = Field(description="Snapshot date")
    total_value: Decimal = Field(description="Portfolio value on this date")
    total_invested: Decimal = Field(description="Cumulative invested amount")
    daily_change: Decimal = Field(description="Day-over-day change in KES")
    daily_change_pct: Decimal = Field(description="Day-over-day change percentage")
