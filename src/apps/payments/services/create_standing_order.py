from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.models import StandingOrder, StandingOrderStatus
from apps.payments.providers.ratiba import RatibaProvider
from apps.payments.services.account_reference import generate_account_reference


def create_standing_order(
    *,
    user_id: UUID,
    plan_id: UUID,
    amount: Decimal,
    frequency: str,
    phone_number: str,
    description: str,
) -> StandingOrder:
    """Ask Safaricom for a standing order backing a recurring plan.

    The row is written before the call so a Ratiba callback that beats our own
    response still finds something to attach to. If Safaricom then rejects the
    request the row is marked FAILED rather than deleted — a standing order we
    may have created is not something to lose track of.
    """
    reference = generate_account_reference()
    # Tomorrow, not today: a StartDate of today is rejected once Safaricom's
    # cut-off for the day has passed, and that cut-off is not published.
    start = timezone.localdate() + timedelta(days=1)
    end = start + timedelta(days=settings.MPESA_RATIBA_DURATION_DAYS)

    order = StandingOrder.objects.create(
        user_id=user_id,
        recurring_plan_id=plan_id,
        account_reference=reference,
        standing_order_name=f"Belong {reference}",
        amount=amount,
        frequency=frequency,
        start_date=start,
        end_date=end,
        phone_number=phone_number,
        status=StandingOrderStatus.PENDING,
    )

    try:
        result = RatibaProvider().create_standing_order(
            custom_sto_id=order.custom_sto_id,
            name=order.standing_order_name,
            amount=amount,
            phone_number=phone_number,
            frequency=frequency,
            start=start,
            end=end,
            account_reference=reference,
            description=description,
        )
    except Exception as e:
        order.status = StandingOrderStatus.FAILED
        order.failure_reason = str(e)
        order.save(update_fields=["status", "failure_reason", "updated_at"])
        raise

    order.response_ref_id = result.response_ref_id
    order.provider_response = result.raw_response
    order.save(update_fields=["response_ref_id", "provider_response", "updated_at"])

    create_audit_log(
        action=AuditAction.STANDING_ORDER_CREATED,
        actor_id=user_id,
        entity_type="StandingOrder",
        entity_id=order.id,
        new_values={
            "account_reference": reference,
            "amount": str(amount),
            "frequency": frequency,
        },
    )
    return order
