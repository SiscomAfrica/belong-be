from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.common.observability import report_exception

logger = logging.getLogger(__name__)


@shared_task(name="apps.investments.tasks.execute_due_recurring_plans")
def execute_due_recurring_plans() -> int:
    """Invest every due contribution that has been funded.

    The money arrives separately, via an M-Pesa Ratiba standing order crediting
    the user's wallet. This job only moves it from wallet to fund, so a plan
    whose deduction has not landed is skipped and retried tomorrow rather than
    failed.
    """
    from apps.investments.models.recurring_plan import RecurringPlan
    from apps.investments.selectors.get_min_contribution import get_min_contribution
    from apps.investments.services.execute_recurring_plan import execute_recurring_plan

    # localdate(), not date.today(): the container runs UTC while the project
    # is Africa/Nairobi (UTC+3), so a naive today() can be a day behind and
    # skip plans that are due.
    today = timezone.localdate()
    plans = RecurringPlan.objects.filter(
        is_active=True, next_run_date__lte=today
    ).select_related("fund", "user")

    # Read once for the whole batch rather than per plan.
    floor = get_min_contribution()

    executed = 0
    unfunded = 0
    for plan in plans:
        try:
            if execute_recurring_plan(plan=plan, min_contribution=floor):
                executed += 1
            else:
                unfunded += 1
        except Exception:
            # One bad plan must not stop the rest of the run, but a recurring
            # investment silently not executing is exactly the sort of failure
            # a user only notices months later.
            report_exception(
                message="Recurring plan execution failed",
                logger_=logger,
                plan_id=plan.id,
            )

    logger.info(
        "Recurring plans: %d executed, %d awaiting funds", executed, unfunded,
    )
    return executed
