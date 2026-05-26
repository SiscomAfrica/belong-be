from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.investments.models.recurring_plan import RecurringPlan


def list_user_plans(
    *, user_id: UUID, is_active: bool | None = None
) -> QuerySet[RecurringPlan]:
    qs = RecurringPlan.objects.filter(user_id=user_id).select_related("fund")
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs
