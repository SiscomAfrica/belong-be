from __future__ import annotations

from decimal import Decimal

import pytest

from apps.payments.models import StandingOrderCharge, StandingOrderStatus
from apps.payments.services.process_ratiba_callback import process_ratiba_callback
from apps.payments.tests.helpers import balance
from apps.payments.tests.ratiba_payloads import creation, execution

pytestmark = pytest.mark.django_db


def test_one_failed_cycle_does_not_kill_a_live_standing_order(
    user, standing_order,
) -> None:
    """A month with no funds is not a reason to tear down auto-invest."""
    ref = str(standing_order.custom_sto_id)
    process_ratiba_callback(payload=creation(ref=ref))
    process_ratiba_callback(payload=execution(ref=ref))

    failed = execution(ref=ref, receipt="0000000000")
    failed["responseBody"]["responseData"][-1] = {"name": "Status", "value": "ERROR"}
    process_ratiba_callback(payload=failed)

    standing_order.refresh_from_db()
    assert standing_order.status == StandingOrderStatus.ACTIVE
    assert balance(user.id) == Decimal("500.00")


def test_a_retried_deduction_does_not_credit_twice(user, standing_order) -> None:
    """Safaricom retries anything it does not see a 200 for."""
    ref = str(standing_order.custom_sto_id)
    process_ratiba_callback(payload=creation(ref=ref))
    payload = execution(ref=ref)

    process_ratiba_callback(payload=payload)
    process_ratiba_callback(payload=payload)

    assert balance(user.id) == Decimal("500.00")


def test_an_unattributable_callback_credits_nobody(user, standing_order) -> None:
    process_ratiba_callback(
        payload=execution(ref="dcb1d1b4-0000-4000-8000-000000000000")
    )

    assert balance(user.id) == Decimal("0.00")
    assert StandingOrderCharge.objects.count() == 0


def test_the_account_reference_resolves_when_the_refs_do_not(
    user, standing_order,
) -> None:
    payload = execution(ref="dcb1d1b4-0000-4000-8000-000000000000")
    payload["responseBody"]["responseData"].append(
        {"name": "AccountReference", "value": standing_order.account_reference},
    )

    process_ratiba_callback(payload=payload)

    # Resolved while still PENDING, so it is read as the creation result.
    standing_order.refresh_from_db()
    assert standing_order.status == StandingOrderStatus.ACTIVE
    assert balance(user.id) == Decimal("0.00")
