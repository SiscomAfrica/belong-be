from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.funds.models import Fund
from apps.investments.exceptions import DuplicateActivePlanError, FundNotActiveError
from apps.investments.models.recurring_plan import PlanFrequency, RecurringPlan

FREQUENCY_OFFSETS = {
    PlanFrequency.DAILY: timedelta(days=1),
    PlanFrequency.WEEKLY: timedelta(weeks=1),
    PlanFrequency.BIWEEKLY: timedelta(weeks=2),
    PlanFrequency.MONTHLY: timedelta(days=30),
}


def create_recurring_plan(
    *, user_id: UUID, fund_id: UUID, amount: Decimal, frequency: str
) -> RecurringPlan:
    fund = Fund.objects.get(id=fund_id)
    if not fund.is_active:
        raise FundNotActiveError()

    exists = RecurringPlan.objects.filter(
        user_id=user_id, fund_id=fund_id, is_active=True
    ).exists()
    if exists:
        raise DuplicateActivePlanError()

    next_run = date.today() + FREQUENCY_OFFSETS[frequency]
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
    return plan
