from __future__ import annotations

from decimal import ROUND_UP, Decimal
from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.payments.providers import get_provider


def topup_amount(amount: Decimal) -> Decimal:
    """M-Pesa accepts whole shillings only.

    Rounds *up*, unlike a Ratiba deduction. This is money the user is being
    asked to add so a contribution can go through, so landing a shilling over
    leaves the plan fundable; landing under leaves it stuck.
    """
    return amount.quantize(Decimal("1"), rounding=ROUND_UP)


def initiate_wallet_topup(
    *,
    user_id: UUID,
    amount: Decimal,
    provider: str,
    phone_number: str,
    idempotency_key: str,
) -> PaymentTransaction:
    """Start a payment that credits the wallet instead of buying units.

    The resulting transaction has no investment, which is exactly what
    settle_successful_payment treats as a top-up. Both this and an M-Pesa
    Ratiba deduction therefore land in the same place by the same code.
    """
    existing = PaymentTransaction.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    charged = topup_amount(amount)
    payment_provider = get_provider(provider)
    result = payment_provider.initiate_payment(
        amount=charged,
        phone_number=phone_number,
        reference=idempotency_key,
    )

    txn = PaymentTransaction.objects.create(
        user_id=user_id,
        investment=None,
        provider=provider,
        status=PaymentStatus.INITIATED,
        amount=charged,
        phone_number=phone_number,
        external_ref=result.external_ref,
        merchant_request_id=result.merchant_request_id,
        authorization_url=result.authorization_url,
        provider_response=result.raw_response,
        idempotency_key=idempotency_key,
    )

    create_audit_log(
        action=AuditAction.PAYMENT_INITIATED,
        actor_id=user_id,
        entity_type="PaymentTransaction",
        entity_id=txn.id,
        new_values={"provider": provider, "amount": str(charged), "kind": "WALLET_TOPUP"},
    )
    return txn
