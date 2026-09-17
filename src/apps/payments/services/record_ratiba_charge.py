from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.payments.models import ChargeStatus, StandingOrder, StandingOrderCharge
from apps.payments.providers.ratiba_request import ratiba_amount
from apps.payments.providers.ratiba_result import RatibaCallbackResult


def charge_idempotency_key(*, order: StandingOrder, result: RatibaCallbackResult) -> str:
    """Stable key for one deduction attempt.

    Successful deductions carry an M-PESA receipt, which is unique forever.
    Failures report the sentinel "0000000000" for every customer, so those are
    keyed per order per day instead — a retried delivery of the same failure
    collapses onto one row, while a genuine failure in the next cycle gets its
    own.
    """
    if result.transaction_id:
        return result.transaction_id
    return f"FAIL-{order.id}-{timezone.localdate().isoformat()}"


def record_ratiba_charge(
    *, order: StandingOrder, result: RatibaCallbackResult, kind: str,
) -> tuple[StandingOrderCharge, bool]:
    """Insert the charge if it is new. Returns (charge, created)."""
    # Ratiba only ever deducts whole shillings, so when the callback omits the
    # amount the truthful fallback is the rounded-down order amount, not the
    # plan amount someone typed.
    amount: Decimal = (
        result.amount
        if result.amount is not None
        else Decimal(ratiba_amount(order.amount))
    )

    return StandingOrderCharge.objects.get_or_create(
        transaction_id=charge_idempotency_key(order=order, result=result),
        defaults={
            "standing_order": order,
            "kind": kind,
            "amount": amount,
            "status": ChargeStatus.OKAY if result.success else ChargeStatus.ERROR,
            "response_code": result.response_code,
            "masked_msisdn": result.masked_msisdn,
            "raw_payload": result.raw_data,
        },
    )
