from __future__ import annotations

from apps.investments.models.recurring_plan import RecurringPlan


def request_plan_funds(*, plan: RecurringPlan) -> None:
    """Ask for exactly what is missing, not the whole contribution.

    A wallet holding part of the amount — a short Ratiba deduction, or a
    manual top-up that did not cover it — should be topped up to the line,
    not charged twice over.
    """
    from apps.investments.services.request_contribution_funds import (
        request_contribution_funds,
    )
    from apps.payments.services.get_or_create_wallet import get_or_create_wallet

    shortfall = plan.amount - get_or_create_wallet(user_id=plan.user_id).balance_ksh
    if shortfall <= 0:
        # The balance arrived between the failed debit and now; the next run
        # will sweep it.
        return

    request_contribution_funds(plan=plan, shortfall=shortfall)
