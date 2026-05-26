from __future__ import annotations

import logging
from datetime import date

from celery import shared_task

from apps.investments.services.create_recurring_plan import FREQUENCY_OFFSETS

logger = logging.getLogger(__name__)


@shared_task(name="apps.investments.tasks.execute_due_recurring_plans")
def execute_due_recurring_plans() -> int:
    from apps.investments.models.recurring_plan import RecurringPlan
    from apps.investments.services.create_investment import create_investment
    from apps.notifications.models import Notification, NotificationType

    today = date.today()
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
            logger.exception("Failed recurring plan %s", plan.id)

    logger.info("Executed %d recurring plans", executed)
    return executed
