from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.common.observability import report_exception
from apps.investments.services.create_recurring_plan import FREQUENCY_OFFSETS

logger = logging.getLogger(__name__)


@shared_task(name="apps.investments.tasks.execute_due_recurring_plans")
def execute_due_recurring_plans() -> int:
    from apps.investments.models.recurring_plan import RecurringPlan
    from apps.investments.services.create_investment import create_investment
    from apps.notifications.models import Notification, NotificationType

    # localdate(), not date.today(): the container runs UTC while the project
    # is Africa/Nairobi (UTC+3), so a naive today() can be a day behind and
    # skip plans that are due.
    today = timezone.localdate()
    plans = RecurringPlan.objects.filter(
        is_active=True, next_run_date__lte=today
    ).select_related("fund")

    executed = 0
    for plan in plans:
        key = f"recurring-{plan.id}-{plan.next_run_date}"
        try:
            create_investment(
                user_id=plan.user_id,
                fund_id=plan.fund_id,
                amount=plan.amount,
                idempotency_key=key,
            )
            Notification.objects.create(
                user_id=plan.user_id,
                type=NotificationType.RECURRING_PLAN_EXECUTED,
                title="Recurring investment executed",
                body=f"Invested {plan.amount} in {plan.fund.name}.",
            )
            plan.next_run_date += FREQUENCY_OFFSETS[plan.frequency]
            plan.save(update_fields=["next_run_date", "updated_at"])
            executed += 1
        except Exception:
            # One bad plan must not stop the rest of the run, but a recurring
            # investment silently not executing is exactly the sort of failure
            # a user only notices months later.
            report_exception(
                message="Recurring plan execution failed",
                logger_=logger,
                plan_id=plan.id,
            )

    logger.info("Executed %d recurring plans", executed)
    return executed
