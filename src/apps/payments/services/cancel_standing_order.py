from __future__ import annotations

from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.models import StandingOrder, StandingOrderStatus

_LIVE = (StandingOrderStatus.PENDING, StandingOrderStatus.ACTIVE)


def cancel_standing_order(*, plan_id: UUID, actor_id: UUID) -> StandingOrder | None:
    """Stop treating a plan's standing order as live.

    Daraja publishes no endpoint for cancelling a standing order — only the
    customer can, from the M-PESA menu. So this marks our side cancelled and
    nothing more, and Safaricom may keep deducting.

    That is survivable only because a deduction credits the wallet rather than
    buying units directly: money from a cancelled plan lands as a balance the
    user can withdraw, instead of being invested in a fund they opted out of.
    The app must still tell them to cancel it in M-PESA.
    """
    order = (
        StandingOrder.objects.filter(recurring_plan_id=plan_id, status__in=_LIVE)
        .order_by("-created_at")
        .first()
    )
    if order is None:
        return None

    order.status = StandingOrderStatus.CANCELLED
    order.save(update_fields=["status", "updated_at"])

    create_audit_log(
        action=AuditAction.STANDING_ORDER_CANCELLED,
        actor_id=actor_id,
        entity_type="StandingOrder",
        entity_id=order.id,
        new_values={"status": StandingOrderStatus.CANCELLED},
    )
    return order
