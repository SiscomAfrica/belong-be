from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.investments.services.cancel_investment import cancel_investment
from apps.payments.models import PaymentStatus, PaymentTransaction


@shared_task(name="apps.payments.tasks.reconcile_pending_payments")
def reconcile_pending_payments() -> int:
    cutoff = timezone.now() - timedelta(minutes=15)
    stale = PaymentTransaction.objects.filter(
        status=PaymentStatus.INITIATED,
        created_at__lt=cutoff,
    )

    count = 0
    for txn in stale.iterator():
        txn.status = PaymentStatus.EXPIRED
        txn.failure_reason = "Payment expired after 15 minutes."
        txn.save(update_fields=["status", "failure_reason", "updated_at"])

        if txn.investment_id:
            cancel_investment(investment_id=txn.investment_id, user_id=txn.user_id)

        count += 1

    return count
