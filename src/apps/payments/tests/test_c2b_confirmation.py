from __future__ import annotations

from decimal import Decimal

import pytest

from apps.payments.models import ChargeKind, StandingOrderCharge
from apps.payments.services.process_c2b_confirmation import process_c2b_confirmation
from apps.payments.tests.helpers import balance

pytestmark = pytest.mark.django_db


def _payment(*, bill_ref: str, trans_id: str = "RKTQDM7W6S", amount: str = "500") -> dict:
    """Daraja's C2B confirmation shape."""
    return {
        "TransactionType": "Pay Bill",
        "TransID": trans_id,
        "TransTime": "20260807063845",
        "TransAmount": amount,
        "BusinessShortCode": "4148853",
        "BillRefNumber": bill_ref,
        "InvoiceNumber": "",
        "OrgAccountBalance": "",
        "ThirdPartyTransID": "",
        "MSISDN": "25470****149",
        "FirstName": "John",
    }


def test_a_ratiba_execution_credits_the_wallet(user, standing_order) -> None:
    """This, not the Ratiba callback, is how a deduction reaches us."""
    process_c2b_confirmation(
        payload=_payment(bill_ref=standing_order.account_reference)
    )

    assert balance(user.id) == Decimal("500.00")
    assert StandingOrderCharge.objects.get().kind == ChargeKind.DEDUCTION


def test_a_replayed_confirmation_credits_once(user, standing_order) -> None:
    payload = _payment(bill_ref=standing_order.account_reference)

    process_c2b_confirmation(payload=payload)
    process_c2b_confirmation(payload=payload)

    assert balance(user.id) == Decimal("500.00")
    assert StandingOrderCharge.objects.count() == 1


def test_the_amount_paid_is_credited_not_the_plan_amount(user, standing_order) -> None:
    """A part payment credits what actually arrived."""
    process_c2b_confirmation(
        payload=_payment(bill_ref=standing_order.account_reference, amount="150")
    )

    assert balance(user.id) == Decimal("150.00")


def test_an_unknown_reference_credits_nobody(user, standing_order) -> None:
    process_c2b_confirmation(payload=_payment(bill_ref="NOTOURSATALL"))

    assert balance(user.id) == Decimal("0.00")
    assert StandingOrderCharge.objects.count() == 0


def test_a_payment_with_no_receipt_is_not_credited(user, standing_order) -> None:
    payload = _payment(bill_ref=standing_order.account_reference)
    payload["TransID"] = ""

    process_c2b_confirmation(payload=payload)

    assert balance(user.id) == Decimal("0.00")


def test_money_is_never_parsed_through_a_float(user, standing_order) -> None:
    process_c2b_confirmation(
        payload=_payment(bill_ref=standing_order.account_reference, amount="0.10")
    )
    process_c2b_confirmation(
        payload=_payment(
            bill_ref=standing_order.account_reference,
            trans_id="RKTQDM7W6T",
            amount="0.20",
        )
    )

    assert balance(user.id) == Decimal("0.30")
