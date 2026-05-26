from __future__ import annotations

from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.payments.models import WithdrawalRequest, WithdrawalStatus


def process_withdrawal(
    *, withdrawal_id: UUID, action: str, admin_user_id: UUID, notes: str = "",
) -> WithdrawalRequest:
    with transaction.atomic():
        withdrawal = (
            WithdrawalRequest.objects.select_for_update()
            .get(id=withdrawal_id)
        )

        status_map = {
            "approve": WithdrawalStatus.APPROVED,
            "reject": WithdrawalStatus.REJECTED,
            "process": WithdrawalStatus.PROCESSED,
        }
        new_status = status_map.get(action)
        if new_status is None:
            msg = f"Invalid action: {action}"
            raise ValueError(msg)

        withdrawal.status = new_status
        withdrawal.admin_notes = notes
        withdrawal.processed_by_id = admin_user_id
        withdrawal.processed_at = timezone.now()
        withdrawal.save(update_fields=[
            "status", "admin_notes", "processed_by_id", "processed_at", "updated_at",
        ])

    return withdrawal
