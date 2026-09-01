from __future__ import annotations

from django.utils import timezone

from apps.investments.models import Investment, InvestmentStatus
from apps.investments.services.cancel_investment import cancel_investment
from apps.investments.services.confirm_investment import confirm_investment
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.payments.services.credit_wallet import credit_wallet


def settle_successful_payment(*, txn: PaymentTransaction) -> None:
    """Apply a confirmed payment exactly once.

    Money lands in one of two places and never both:

    - A payment tied to an investment buys units. The cash is consumed by the
      purchase, so the wallet must not also be credited — doing that counted
      the same money twice, once as cash and once as holdings.
    - A payment with no investment is a wallet top-up, so it credits the wallet
      and nothing else.

    Both rails share this so they cannot drift apart again: M-Pesa previously
    credited *and* confirmed, while Paystack only confirmed and never credited
    a top-up at all.
    """
    txn.status = PaymentStatus.SUCCESS
    txn.completed_at = timezone.now()
    txn.save(update_fields=[
        "status", "provider_response", "completed_at", "updated_at",
    ])

    if not txn.investment_id:
        credit_wallet(user_id=txn.user_id, amount=txn.amount, currency="KES")
        return

    # An investment still awaiting KYC is confirmed later, once KYC clears.
    status = (
        Investment.objects.filter(id=txn.investment_id)
        .values_list("status", flat=True)
        .first()
    )
    if status != InvestmentStatus.PENDING_KYC:
        confirm_investment(investment_id=txn.investment_id)


def settle_failed_payment(*, txn: PaymentTransaction, reason: str) -> None:
    """Mark a payment failed and release whatever it was holding."""
    txn.status = PaymentStatus.FAILED
    txn.failure_reason = reason
    txn.completed_at = timezone.now()
    txn.save(update_fields=[
        "status", "failure_reason", "provider_response", "completed_at", "updated_at",
    ])

    if txn.investment_id:
        cancel_investment(investment_id=txn.investment_id, user_id=txn.user_id)
