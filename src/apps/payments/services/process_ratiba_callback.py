from __future__ import annotations

import logging

from django.db import transaction

from apps.common.observability import report_exception
from apps.payments.models import ChargeKind, StandingOrder, StandingOrderStatus
from apps.payments.providers.ratiba_callback import parse_ratiba_callback
from apps.payments.selectors.resolve_standing_order import resolve_standing_order
from apps.payments.services.credit_wallet import credit_wallet
from apps.payments.services.ratiba_audit import audit_callback
from apps.payments.services.ratiba_notifications import notify_callback
from apps.payments.services.record_ratiba_charge import record_ratiba_charge
from apps.payments.services.update_standing_order_state import (
    activate_standing_order,
    fail_standing_order,
)

logger = logging.getLogger(__name__)


def process_ratiba_callback(*, payload: dict) -> None:
    """Apply one M-Pesa Ratiba callback.

    Two different events arrive on this URL wearing the same payload shape,
    and telling them apart is the whole job:

    - The *creation* result, which Daraja documents. It reports Status=OKAY
      and carries the standing order's Amount, but no money has moved — the
      first execution happens on StartDate. Crediting it would invent cash.
    - An *execution*, if Daraja sends one. That is real money.

    The standing order's own state separates them: a callback arriving while
    we are still PENDING can only be the creation result, because nothing can
    execute before the customer has approved the prompt.
    """
    result = parse_ratiba_callback(payload=payload)
    order = resolve_standing_order(result=result)

    if order is None:
        # Money may have genuinely left a customer's account and we cannot say
        # whose. That is a reconciliation break, not a log line to scroll past.
        report_exception(
            message="Unattributable M-Pesa Ratiba callback",
            logger_=logger,
            request_ref_id=result.request_ref_id,
            response_ref_id=result.response_ref_id,
            account_reference=result.account_reference,
        )
        return

    with transaction.atomic():
        locked = StandingOrder.objects.select_for_update().get(id=order.id)
        is_activation = locked.status == StandingOrderStatus.PENDING
        kind = ChargeKind.ACTIVATION if is_activation else ChargeKind.DEDUCTION

        charge, created = record_ratiba_charge(
            order=locked, result=result, kind=kind,
        )
        if not created:
            # Safaricom retried a delivery we have already applied. This is
            # also what stops a replayed creation callback being mistaken for
            # a deduction now that the order is ACTIVE.
            return

        if result.success and is_activation:
            activate_standing_order(order=locked, result=result)
        elif result.success:
            credit_wallet(user_id=locked.user_id, amount=charge.amount, currency="KES")
        elif is_activation:
            # The customer never approved the prompt, so the order was never
            # live. A failure on an already-ACTIVE order is one bad cycle
            # (usually no funds) and must not kill the whole standing order.
            fail_standing_order(order=locked, result=result)

    audit_callback(order=locked, result=result, is_activation=is_activation)
    notify_callback(order=locked, charge=charge, result=result, is_activation=is_activation)
