from __future__ import annotations

import logging
from decimal import Decimal

from apps.common.observability import report_exception
from apps.investments.models.recurring_plan import RecurringPlan
from apps.notifications.models import NotificationType
from apps.notifications.services.create_notification import create_notification

logger = logging.getLogger(__name__)


def request_contribution_funds(*, plan: RecurringPlan, shortfall: Decimal) -> bool:
    """Ask the customer to fund a contribution that has nothing behind it.

    This is the stand-in for M-Pesa Ratiba until Safaricom approves the
    standing order. Where Ratiba deducts silently, this sends an STK prompt the
    customer approves with their PIN — but it credits the wallet through the
    very same path, so the sweep that follows does not know or care which one
    paid. When Ratiba goes live this simply stops being reached.

    Returns True when a prompt was sent.
    """
    from apps.payments.selectors.has_live_standing_order import has_live_standing_order
    from apps.payments.services.initiate_wallet_topup import initiate_wallet_topup

    # A live standing order means Safaricom is already collecting. Prompting as
    # well would take the contribution twice in one cycle.
    if has_live_standing_order(plan_id=plan.id):
        return False

    # One prompt per due date, not one per run: the key is stable, so a plan
    # that stays unfunded for a week is asked once, not seven times.
    key = f"autoinvest-topup-{plan.id}-{plan.next_run_date}"

    try:
        initiate_wallet_topup(
            user_id=plan.user_id,
            amount=shortfall,
            provider="MPESA",
            phone_number=plan.user.phone,
            idempotency_key=key,
        )
    except Exception:
        report_exception(
            message="Could not request funds for a due contribution",
            logger_=logger,
            plan_id=plan.id,
        )
        return False

    create_notification(
        user_id=plan.user_id,
        type=NotificationType.CONTRIBUTION_DUE,
        title="Approve your contribution",
        body=(
            f"Check your phone for an M-PESA prompt for KSh {shortfall} "
            f"to fund your {plan.fund.name} plan."
        ),
        metadata={"plan_id": str(plan.id)},
    )
    return True
