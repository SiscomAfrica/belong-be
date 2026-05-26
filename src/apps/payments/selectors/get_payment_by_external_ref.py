from __future__ import annotations

from apps.payments.exceptions import PaymentNotFoundError
from apps.payments.models import PaymentTransaction


def get_payment_by_external_ref(*, external_ref: str) -> PaymentTransaction:
    try:
        return PaymentTransaction.objects.get(external_ref=external_ref)
    except PaymentTransaction.DoesNotExist:
        raise PaymentNotFoundError() from None
