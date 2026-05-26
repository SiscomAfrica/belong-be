from __future__ import annotations

from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.investments.models.recurring_plan import RecurringPlan
from apps.investments.selectors.get_recurring_plan import get_recurring_plan


def pause_recurring_plan(*, plan_id: UUID, user_id: UUID) -> RecurringPlan:
    plan = get_recurring_plan(plan_id=plan_id, user_id=user_id)
    plan.is_active = False
    plan.save(update_fields=["is_active", "updated_at"])

    create_audit_log(
        action=AuditAction.RECURRING_PLAN_PAUSED,
        actor_id=user_id,
        entity_type="RecurringPlan",
        entity_id=plan.id,
        new_values={"is_active": False},
    )
    return plan
