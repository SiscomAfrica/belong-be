from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.models import WithdrawalRequest


def create_withdrawal_request(
    *, user_id: UUID, amount: Decimal, phone_number: str,
) -> WithdrawalRequest:
    withdrawal = WithdrawalRequest.objects.create(
        user_id=user_id,
        amount=amount,
        phone_number=phone_number,
    )

    create_audit_log(
        action=AuditAction.WITHDRAWAL_REQUESTED,
        actor_id=user_id,
        entity_type="WithdrawalRequest",
        entity_id=withdrawal.id,
        new_values={"amount": str(amount), "phone_number": phone_number},
    )

    return withdrawal
