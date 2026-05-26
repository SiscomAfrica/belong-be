from __future__ import annotations

from uuid import UUID

from apps.investments.exceptions import PlanNotFoundError
from apps.investments.models.recurring_plan import RecurringPlan


def get_recurring_plan(*, plan_id: UUID, user_id: UUID) -> RecurringPlan:
    try:
        return RecurringPlan.objects.select_related("fund").get(
            id=plan_id, user_id=user_id
        )
    except RecurringPlan.DoesNotExist:
        raise PlanNotFoundError()
