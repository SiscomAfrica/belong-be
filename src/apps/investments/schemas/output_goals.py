from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class GoalFundOut(Schema):
    id: UUID = Field(description="Fund identifier")
    name: str = Field(description="Fund display name")
    slug: str = Field(description="URL-safe fund slug")


class InvestmentGoalOut(Schema):
    id: UUID = Field(description="Goal identifier")
    fund: GoalFundOut = Field(description="Associated fund summary")
    target_amount: Decimal = Field(description="Goal target amount in KES")
    current_value: Decimal = Field(description="Current invested value toward this goal")
    target_date: date = Field(description="Target completion date")
    progress_pct: Decimal = Field(description="Progress toward goal as a percentage")
    created_at: datetime = Field(description="Goal creation timestamp")

    @staticmethod
    def resolve_fund(obj) -> dict:  # noqa: ANN001
        return {"id": obj.fund.id, "name": obj.fund.name, "slug": obj.fund.slug}

    @staticmethod
    def resolve_current_value(obj) -> Decimal:  # noqa: ANN001
        return getattr(obj, "current_value", Decimal("0"))

    @staticmethod
    def resolve_progress_pct(obj) -> Decimal:  # noqa: ANN001
        current = getattr(obj, "current_value", Decimal("0"))
        if obj.target_amount > 0:
            return round((current / obj.target_amount) * 100, 2)
        return Decimal("0")


class GoalListOut(Schema):
    items: list[InvestmentGoalOut] = Field(description="List of investment goals")
    count: int = Field(description="Total number of goals")
