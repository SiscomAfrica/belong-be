from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.utils import timezone

from apps.investments.exceptions import PlanNotActiveError, StandingOrderLockedError
from apps.investments.models.recurring_plan import RecurringPlan
from apps.investments.selectors.get_recurring_plan import get_recurring_plan
from apps.investments.services.plan_schedule import next_run_after


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

    if (amount is not None or frequency is not None) and _has_live_standing_order(plan):
        # Daraja can neither amend nor cancel a standing order — only the
        # customer can, from the M-PESA menu. Writing a new amount here would
        # leave Safaricom deducting the old one against a plan that claims the
        # new one, or deducting both if a second order were created. Refusing
        # is the only option that cannot take money the user did not agree to.
        raise StandingOrderLockedError()

    update_fields = ["updated_at"]

    if amount is not None:
        plan.amount = amount
        update_fields.append("amount")

    if frequency is not None:
        plan.frequency = frequency
        # localdate(), not date.today(): the container runs UTC while the
        # project is Africa/Nairobi, so a naive today() reschedules a day early
        # between midnight and 03:00 EAT.
        today = timezone.localdate()
        plan.next_run_date = next_run_after(start=today, frequency=frequency) or today
        update_fields.extend(["frequency", "next_run_date"])

    plan.save(update_fields=update_fields)
    return plan


def _has_live_standing_order(plan: RecurringPlan) -> bool:
    from apps.payments.selectors.has_live_standing_order import has_live_standing_order

    return has_live_standing_order(plan_id=plan.id)
