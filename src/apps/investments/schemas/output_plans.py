from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.investments.models.recurring_plan import RecurringPlan


class PlanFundOut(Schema):
    id: UUID = Field(description="Fund identifier")
    name: str = Field(description="Fund display name")
    slug: str = Field(description="URL-safe fund slug")


class RecurringPlanOut(Schema):
    id: UUID = Field(description="Recurring plan identifier")
    fund: PlanFundOut = Field(description="Associated fund summary")
    amount: Decimal = Field(description="Amount invested per execution in KES")
    frequency: str = Field(description="Execution frequency: DAILY | WEEKLY | BIWEEKLY | MONTHLY")
    next_run_date: date = Field(description="Next scheduled execution date")
    is_active: bool = Field(description="Whether the plan is currently active")
    created_at: datetime = Field(description="Plan creation timestamp")

    @staticmethod
    def resolve_fund(obj: RecurringPlan) -> dict:
        return {"id": obj.fund.id, "name": obj.fund.name, "slug": obj.fund.slug}


class PlanListOut(Schema):
    items: list[RecurringPlanOut] = Field(description="List of recurring plans")
    count: int = Field(description="Total number of plans")
