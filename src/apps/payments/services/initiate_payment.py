from __future__ import annotations

from uuid import UUID

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.investments.models import Investment, InvestmentStatus
from apps.payments.exceptions import (
    InvestmentNotPendingError,
    PaymentAlreadyInitiatedError,
)
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.payments.providers import get_provider


def initiate_payment(
    *,
    user_id: UUID,
    investment_id: UUID,
    provider: str,
    phone_number: str,
    idempotency_key: str,
) -> PaymentTransaction:
    existing = PaymentTransaction.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    with transaction.atomic():
        investment = (
            Investment.objects.select_for_update()
            .get(id=investment_id, user_id=user_id)
        )
        if investment.status != InvestmentStatus.PENDING:
            raise InvestmentNotPendingError()

        has_active = PaymentTransaction.objects.filter(
            investment_id=investment_id, status=PaymentStatus.INITIATED,
        ).exists()
        if has_active:
            raise PaymentAlreadyInitiatedError()

        payment_provider = get_provider(provider)
        result = payment_provider.initiate_payment(
            amount=investment.amount,
            phone_number=phone_number,
            reference=idempotency_key,
        )

        txn = PaymentTransaction.objects.create(
            user_id=user_id,
            investment=investment,
            provider=provider,
            status=PaymentStatus.INITIATED,
            amount=investment.amount,
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
        new_values={"provider": provider, "amount": str(investment.amount)},
    )

    return txn
