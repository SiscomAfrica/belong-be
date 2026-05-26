from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from apps.investments.exceptions import PlanNotActiveError
from apps.investments.models.recurring_plan import RecurringPlan
from apps.investments.selectors.get_recurring_plan import get_recurring_plan
from apps.investments.services.create_recurring_plan import FREQUENCY_OFFSETS


def update_recurring_plan(
    *,
    plan_id: UUID,
    user_id: UUID,
    amount: Decimal | None = None,
    frequency: str | None = None,
) -> RecurringPlan:
    plan = get_recurring_plan(plan_id=plan_id, user_id=user_id)
    if not plan.is_active:
        raise PlanNotActiveError()

    update_fields = ["updated_at"]

    if amount is not None:
        plan.amount = amount
        update_fields.append("amount")

    if frequency is not None:
        plan.frequency = frequency
        plan.next_run_date = date.today() + FREQUENCY_OFFSETS[frequency]
        update_fields.extend(["frequency", "next_run_date"])

    plan.save(update_fields=update_fields)
    return plan
