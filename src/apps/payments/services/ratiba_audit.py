from __future__ import annotations

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.models import StandingOrder
from apps.payments.providers.ratiba_result import RatibaCallbackResult


def audit_callback(
    *, order: StandingOrder, result: RatibaCallbackResult, is_activation: bool,
) -> None:
    if result.success and is_activation:
        action = AuditAction.STANDING_ORDER_ACTIVATED
    elif result.success:
        action = AuditAction.STANDING_ORDER_CHARGED
    else:
        action = AuditAction.STANDING_ORDER_CHARGE_FAILED

    create_audit_log(
        action=action,
        actor_id=order.user_id,
        entity_type="StandingOrder",
        entity_id=order.id,
        new_values={
            "account_reference": order.account_reference,
            "transaction_id": result.transaction_id,
            "response_code": result.response_code,
            "reminder_schedule_id": result.reminder_schedule_id,
        },
    )
