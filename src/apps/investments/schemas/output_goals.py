from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class GoalFundOut(Schema):
    id: UUID
    name: str
    slug: str


class InvestmentGoalOut(Schema):
    id: UUID
    fund: GoalFundOut
    target_amount: Decimal
    current_value: Decimal
    target_date: date
    progress_pct: Decimal
    created_at: datetime

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
    items: list[InvestmentGoalOut]
    count: int
