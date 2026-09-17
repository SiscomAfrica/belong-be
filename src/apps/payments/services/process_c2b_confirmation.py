from __future__ import annotations

import logging

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.common.observability import report_exception
from apps.payments.models import (
    ChargeKind,
    ChargeStatus,
    StandingOrder,
    StandingOrderCharge,
)
from apps.payments.providers.c2b_confirmation import parse_c2b_confirmation
from apps.payments.services.credit_wallet import credit_wallet

logger = logging.getLogger(__name__)


def process_c2b_confirmation(*, payload: dict) -> None:
    """Credit a paybill payment to the wallet it belongs to.

    An M-Pesa Ratiba execution arrives here, not on the Ratiba callback URL:
    the standing order pays the shortcode like any other customer, quoting the
    AccountReference we generated as BillRefNumber. Daraja's Ratiba callback
    reports only whether the order was *created*.
    """
    result = parse_c2b_confirmation(payload=payload)

    if not result.trans_id or result.amount is None:
        report_exception(
            message="C2B confirmation missing a receipt or amount",
            logger_=logger,
            bill_ref=result.bill_ref,
        )
        return

    order = (
        StandingOrder.objects.filter(account_reference=result.bill_ref).first()
        if result.bill_ref
        else None
    )

    if order is None:
        # Somebody paid the paybill with a reference we did not issue. Real
        # money we cannot attribute is a reconciliation break, not a log line.
        report_exception(
            message="Unattributable C2B payment",
            logger_=logger,
            trans_id=result.trans_id,
            bill_ref=result.bill_ref,
            amount=str(result.amount),
        )
        return

    with transaction.atomic():
        locked = StandingOrder.objects.select_for_update().get(id=order.id)
        _, created = StandingOrderCharge.objects.get_or_create(
            # The M-PESA receipt is unique forever, so a replayed confirmation
            # inserts nothing and credits nothing.
            transaction_id=result.trans_id,
            defaults={
                "standing_order": locked,
                "kind": ChargeKind.DEDUCTION,
                "amount": result.amount,
                "status": ChargeStatus.OKAY,
                "masked_msisdn": result.msisdn,
                "raw_payload": result.raw_data,
            },
        )
        if not created:
            return

        credit_wallet(user_id=locked.user_id, amount=result.amount, currency="KES")

    create_audit_log(
        action=AuditAction.STANDING_ORDER_CHARGED,
        actor_id=locked.user_id,
        entity_type="StandingOrder",
        entity_id=locked.id,
        new_values={
            "trans_id": result.trans_id,
            "bill_ref": result.bill_ref,
            "amount": str(result.amount),
        },
    )
