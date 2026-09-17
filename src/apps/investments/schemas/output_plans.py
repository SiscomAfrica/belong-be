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
    frequency: str = Field(
        description=(
            "Contribution cadence: ONE_OFF | DAILY | WEEKLY | BIWEEKLY | "
            "MONTHLY | BIMONTHLY | QUARTERLY | HALF_YEARLY | YEARLY"
        ),
    )
    next_run_date: date = Field(description="Next scheduled execution date")
    is_active: bool = Field(description="Whether the plan is currently active")
    # The app needs this to distinguish "auto-invest is running" from "we are
    # still waiting for the customer to approve the M-PESA prompt".
    standing_order_status: str = Field(
        description=(
            "M-Pesa Ratiba standing order state: PENDING (awaiting the "
            "customer's M-PESA PIN approval), ACTIVE, FAILED, CANCELLED, "
            "COMPLETED, or NONE when the plan has no standing order"
        ),
    )
    created_at: datetime = Field(description="Plan creation timestamp")

    @staticmethod
    def resolve_fund(obj: RecurringPlan) -> dict:
        return {"id": obj.fund.id, "name": obj.fund.name, "slug": obj.fund.slug}

    @staticmethod
    def resolve_standing_order_status(obj: RecurringPlan) -> str:
        from apps.payments.selectors.get_plan_standing_order import (
            get_plan_standing_order_status,
        )

        return get_plan_standing_order_status(plan=obj)


class PlanListOut(Schema):
    items: list[RecurringPlanOut] = Field(description="List of recurring plans")
    count: int = Field(description="Total number of plans")
