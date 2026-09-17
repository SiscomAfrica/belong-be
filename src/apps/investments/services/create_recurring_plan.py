from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.funds.models import Fund
from apps.investments.exceptions import (
    BelowMinimumContributionError,
    DuplicateActivePlanError,
    FundNotActiveError,
)
from apps.investments.models.recurring_plan import RecurringPlan
from apps.investments.selectors.get_min_contribution import get_min_contribution
from apps.investments.services.plan_schedule import next_run_after


def create_recurring_plan(
    *, user_id: UUID, fund_id: UUID, amount: Decimal, frequency: str, phone_number: str
) -> RecurringPlan:
    minimum = get_min_contribution()
    if amount < minimum:
        raise BelowMinimumContributionError(str(minimum))

    fund = Fund.objects.get(id=fund_id)
    if not fund.is_active:
        raise FundNotActiveError()

    exists = RecurringPlan.objects.filter(
        user_id=user_id, fund_id=fund_id, is_active=True
    ).exists()
    if exists:
        raise DuplicateActivePlanError()

    today = timezone.localdate()
    # A one-off has no following run, so it is due on its own start date.
    next_run = next_run_after(start=today, frequency=frequency) or today

    plan = RecurringPlan.objects.create(
        user_id=user_id,
        fund_id=fund_id,
        amount=amount,
        frequency=frequency,
        next_run_date=next_run,
    )

    create_audit_log(
        action=AuditAction.RECURRING_PLAN_CREATED,
        actor_id=user_id,
        entity_type="RecurringPlan",
        entity_id=plan.id,
        new_values={"fund_id": str(fund_id), "amount": str(amount)},
    )

    _attach_standing_order(
        plan=plan, fund=fund, amount=amount, frequency=frequency,
        phone_number=phone_number,
    )
    return plan


def _attach_standing_order(
    *, plan: RecurringPlan, fund: Fund, amount: Decimal,
    frequency: str, phone_number: str,
) -> None:
    """Set up the M-Pesa Ratiba deduction that funds this plan.

    Deliberately not in the same transaction as the plan: when Safaricom
    rejects the request the FAILED standing-order row is the only record of
    what was attempted, and a rollback would erase it. The plan is deactivated
    instead, so nothing is left looking live without a way to collect money.
    """
    if not getattr(settings, "MPESA_RATIBA_ENABLED", False):
        return

    from apps.payments.services.create_standing_order import create_standing_order

    try:
        create_standing_order(
            user_id=plan.user_id,
            plan_id=plan.id,
            amount=amount,
            frequency=frequency,
            phone_number=phone_number,
            description=fund.name,
        )
    except Exception:
        plan.is_active = False
        plan.save(update_fields=["is_active", "updated_at"])
        raise
