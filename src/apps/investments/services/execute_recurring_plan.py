from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.investments.models import Investment, InvestmentStatus
from apps.investments.models.recurring_plan import RecurringPlan
from apps.investments.selectors.get_min_contribution import get_min_contribution
from apps.investments.services.confirm_investment import confirm_investment
from apps.investments.services.create_investment import create_investment
from apps.investments.services.plan_schedule import next_run_after
from apps.investments.services.request_plan_funds import request_plan_funds
from apps.notifications.models import NotificationType
from apps.notifications.services.create_notification import create_notification
from apps.payments.exceptions import InsufficientBalanceError
from apps.payments.services.debit_wallet import debit_wallet


def execute_recurring_plan(
    *, plan: RecurringPlan, min_contribution: Decimal | None = None,
) -> bool:
    """Sweep one contribution out of the wallet and into the plan's fund.

    Returns False when the wallet is short. M-Pesa Ratiba collects on
    Safaricom's clock, not ours, so a contribution that has not landed yet is
    expected rather than exceptional: the plan keeps its due date and the next
    run picks it up once the deduction arrives. Nothing is invested on credit.
    """
    floor = (
        get_min_contribution() if min_contribution is None else min_contribution
    )
    key = f"recurring-{plan.id}-{plan.next_run_date}"

    if Investment.objects.filter(idempotency_key=key).exists():
        # A previous run already bought this contribution but did not get as
        # far as advancing the plan. create_investment would hand back the same
        # investment, so debiting first would take the money a second time for
        # units already owned. Move the plan on instead.
        _advance(plan=plan)
        return True

    try:
        with transaction.atomic():
            debit_wallet(user_id=plan.user_id, amount=plan.amount, currency="KES")
            investment = create_investment(
                user_id=plan.user_id,
                fund_id=plan.fund_id,
                amount=plan.amount,
                idempotency_key=key,
                minimum_amount=floor,
            )
            # Mirrors settle_payment: an investment still waiting on KYC is
            # confirmed by activate_pending_investments once KYC clears, never
            # here. Confirming it now would credit units past the KYC gate.
            if investment.status != InvestmentStatus.PENDING_KYC:
                confirm_investment(investment_id=investment.id)
    except InsufficientBalanceError:
        request_plan_funds(plan=plan)
        return False

    create_notification(
        user_id=plan.user_id,
        type=NotificationType.RECURRING_PLAN_EXECUTED,
        title="Recurring investment executed",
        body=f"Invested KSh {plan.amount} in {plan.fund.name}.",
    )

    _advance(plan=plan)
    return True


def _advance(*, plan: RecurringPlan) -> None:
    """Move the plan to its next contribution, or retire a one-off."""
    following = next_run_after(start=plan.next_run_date, frequency=plan.frequency)

    if following is None:
        plan.is_active = False
        plan.save(update_fields=["is_active", "updated_at"])
        return

    plan.next_run_date = following
    plan.save(update_fields=["next_run_date", "updated_at"])
