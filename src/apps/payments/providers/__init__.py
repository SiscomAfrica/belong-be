from __future__ import annotations

from apps.payments.models import PaymentProvider
from apps.payments.providers.base import BasePaymentProvider
from apps.payments.providers.mpesa import MpesaProvider
from apps.payments.providers.paystack import PaystackProvider


def get_provider(provider: str) -> BasePaymentProvider:
    providers = {
        PaymentProvider.MPESA: MpesaProvider,
        PaymentProvider.PAYSTACK: PaystackProvider,
    }
    cls = providers.get(provider)
    if cls is None:
        msg = f"Unknown payment provider: {provider}"
        raise ValueError(msg)
    return cls()


__all__ = ["BasePaymentProvider", "MpesaProvider", "PaystackProvider", "get_provider"]
