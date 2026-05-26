from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.payments.models import WithdrawalRequest


def list_withdrawal_requests(
    *, user_id: UUID, status: str | None = None,
) -> QuerySet[WithdrawalRequest]:
    qs = WithdrawalRequest.objects.filter(user_id=user_id)

    if status:
        qs = qs.filter(status=status)

    return qs
