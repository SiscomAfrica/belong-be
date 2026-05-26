from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.investments.services.cancel_investment import cancel_investment
from apps.investments.services.confirm_investment import confirm_investment
from apps.payments.exceptions import InvalidCallbackError
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.payments.providers.paystack import PaystackProvider


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
        txn.completed_at = timezone.now()

        if result.success:
            txn.status = PaymentStatus.SUCCESS
            txn.save(update_fields=["status", "provider_response", "completed_at", "updated_at"])
            if txn.investment_id:
                confirm_investment(investment_id=txn.investment_id)
            action = AuditAction.PAYMENT_RECEIVED
        else:
            txn.status = PaymentStatus.FAILED
            txn.failure_reason = result.failure_reason
            txn.save(update_fields=[
                "status", "failure_reason", "provider_response", "completed_at", "updated_at",
            ])
            if txn.investment_id:
                cancel_investment(investment_id=txn.investment_id, user_id=txn.user_id)
            action = AuditAction.PAYMENT_FAILED

    create_audit_log(
        action=action,
        actor_id=txn.user_id,
        entity_type="PaymentTransaction",
        entity_id=txn.id,
        new_values={"status": txn.status, "external_ref": txn.external_ref},
    )
