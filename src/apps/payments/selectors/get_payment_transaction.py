from __future__ import annotations

from uuid import UUID

from apps.payments.exceptions import PaymentNotFoundError
from apps.payments.models import PaymentTransaction


def get_payment_transaction(*, transaction_id: UUID, user_id: UUID) -> PaymentTransaction:
    try:
        return (
            PaymentTransaction.objects
            .select_related("investment", "investment__fund")
            .get(id=transaction_id, user_id=user_id)
        )
    except PaymentTransaction.DoesNotExist:
        raise PaymentNotFoundError() from None
