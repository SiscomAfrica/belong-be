from __future__ import annotations

from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.investments.models.recurring_plan import RecurringPlan
from apps.investments.selectors.get_recurring_plan import get_recurring_plan


def pause_recurring_plan(*, plan_id: UUID, user_id: UUID) -> RecurringPlan:
    from apps.payments.services.cancel_standing_order import cancel_standing_order

    plan = get_recurring_plan(plan_id=plan_id, user_id=user_id)
    plan.is_active = False
    plan.save(update_fields=["is_active", "updated_at"])

    # Daraja has no cancel endpoint, so this only stops *us* sweeping the
    # wallet into the fund. Safaricom may keep deducting until the customer
    # cancels the standing order in the M-PESA menu themselves; those
    # deductions land as withdrawable wallet balance, not as investments.
    cancel_standing_order(plan_id=plan.id, actor_id=user_id)

    create_audit_log(
        action=AuditAction.RECURRING_PLAN_PAUSED,
        actor_id=user_id,
        entity_type="RecurringPlan",
        entity_id=plan.id,
        new_values={"is_active": False},
    )
    return plan
