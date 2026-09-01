from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.models import WithdrawalRequest
from apps.payments.services.debit_wallet import debit_wallet


def create_withdrawal_request(
    *, user_id: UUID, amount: Decimal, phone_number: str,
) -> WithdrawalRequest:
    """Reserve funds and record a withdrawal request.

    The balance is debited when the request is made, not when an admin
    approves it. Deferring the debit would let a user queue several
    withdrawals that each pass a balance check individually and overdraw the
    wallet in aggregate. A rejected request returns the funds.

    `debit_wallet` raises InsufficientBalanceError if the balance will not
    cover it, which surfaces to the caller as a 4xx rather than a silent
    negative balance.
    """
    with transaction.atomic():
        debit_wallet(user_id=user_id, amount=amount, currency="KES")

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
