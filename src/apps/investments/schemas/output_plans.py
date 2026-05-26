from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema

from apps.investments.models.recurring_plan import RecurringPlan


class PlanFundOut(Schema):
    id: UUID
    name: str
    slug: str


class RecurringPlanOut(Schema):
    id: UUID
    fund: PlanFundOut
    amount: Decimal
    frequency: str
    next_run_date: date
    is_active: bool
    created_at: datetime

    @staticmethod
    def resolve_fund(obj: RecurringPlan) -> dict:
        return {"id": obj.fund.id, "name": obj.fund.name, "slug": obj.fund.slug}


class PlanListOut(Schema):
    items: list[RecurringPlanOut]
    count: int
