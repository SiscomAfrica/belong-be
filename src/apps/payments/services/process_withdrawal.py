from __future__ import annotations

from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.payments.models import WithdrawalRequest, WithdrawalStatus
from apps.payments.services.credit_wallet import credit_wallet

_ACTIONS = {
    "approve": WithdrawalStatus.APPROVED,
    "reject": WithdrawalStatus.REJECTED,
    "process": WithdrawalStatus.PROCESSED,
}

# Statuses from which the reserved funds have not yet been returned.
_HOLDS_FUNDS = (WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED)


def process_withdrawal(
    *, withdrawal_id: UUID, action: str, admin_user_id: UUID, notes: str = "",
) -> WithdrawalRequest:
    """Advance a withdrawal, returning reserved funds if it is rejected.

    Funds were debited when the request was created, so approving or
    processing moves no money — the balance already reflects it. Rejecting
    must put it back, and must do so only once: a second reject on an
    already-rejected request would credit the user twice.
    """
    with transaction.atomic():
        withdrawal = (
            WithdrawalRequest.objects.select_for_update()
            .get(id=withdrawal_id)
        )

        new_status = _ACTIONS.get(action)
        if new_status is None:
            msg = f"Invalid action: {action}"
            raise ValueError(msg)

        refunding = (
            new_status == WithdrawalStatus.REJECTED
            and withdrawal.status in _HOLDS_FUNDS
        )

        withdrawal.status = new_status
        withdrawal.admin_notes = notes
        withdrawal.processed_by_id = admin_user_id
        withdrawal.processed_at = timezone.now()
        withdrawal.save(update_fields=[
            "status", "admin_notes", "processed_by_id", "processed_at", "updated_at",
        ])

        if refunding:
            credit_wallet(
                user_id=withdrawal.user_id,
                amount=withdrawal.amount,
                currency="KES",
            )

    return withdrawal
