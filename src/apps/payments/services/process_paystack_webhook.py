from __future__ import annotations

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.exceptions import InvalidCallbackError
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.payments.providers.paystack import PaystackProvider
from apps.payments.services.settle_payment import (
    settle_failed_payment,
    settle_successful_payment,
)


def process_paystack_webhook(*, payload: dict, signature: str, body: bytes) -> None:
    PaystackProvider.verify_signature(payload_body=body, signature=signature)

    event = payload.get("event", "")
    if event not in ("charge.success", "charge.failed"):
        return

    result = PaystackProvider().verify_callback(payload=payload)

    if not result.external_ref:
        raise InvalidCallbackError("Missing reference in payload.")

    with transaction.atomic():
        try:
            txn = (
                PaymentTransaction.objects.select_for_update()
                .get(external_ref=result.external_ref)
            )
        except PaymentTransaction.DoesNotExist:
            return

        if txn.status != PaymentStatus.INITIATED:
            return

        txn.provider_response = result.raw_data

        if result.success:
            settle_successful_payment(txn=txn)
            action = AuditAction.PAYMENT_RECEIVED
        else:
            settle_failed_payment(txn=txn, reason=result.failure_reason)
            action = AuditAction.PAYMENT_FAILED

    create_audit_log(
        action=action,
        actor_id=txn.user_id,
        entity_type="PaymentTransaction",
        entity_id=txn.id,
        new_values={"status": txn.status, "external_ref": txn.external_ref},
    )
